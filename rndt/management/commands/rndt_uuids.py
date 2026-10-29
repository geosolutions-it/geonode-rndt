from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from geonode.base.management.command_utils import setup_logger
from geonode.layers.models import Dataset

from rndt.models import GroupProfileRNDT, update_uuids, uuid_mismatches


logger = setup_logger()


class Command(BaseCommand):
    help = "Check or fix the iPA prefix in the uuid of the datasets of the groups with a Pubblica Amministrazione"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("check", "fix"))
        parser.add_argument(
            "datasets",
            nargs="*",
            metavar="id_or_uuid",
            help="Only process these datasets (default: all); datasets in groups without a PA are skipped",
        )

    def handle(self, *args, action, datasets, **options):
        selected = Dataset.objects.all()
        if datasets:
            ids = {int(d) for d in datasets if d.isdigit()}
            uuids = {d for d in datasets if not d.isdigit()}
            selected = selected.filter(Q(id__in=ids) | Q(uuid__in=uuids))
            known = {str(value) for row in selected.values_list("id", "uuid") for value in row}
            for unknown in sorted(set(datasets) - known):
                logger.warning(f"Dataset not found: {unknown}")

        found = 0
        for group_rndt in GroupProfileRNDT.objects.select_related("pa", "group_profile"):
            ipa = group_rndt.pa.ipa
            mismatches = list(uuid_mismatches(selected.filter(group_id=group_rndt.group_profile.group_id), ipa))
            for dataset, new_uuid in mismatches:
                logger.info(f"Dataset {dataset.id} '{dataset.title}': {dataset.uuid} -> {new_uuid}")
            if mismatches and action == "fix":
                update_uuids([dataset for dataset, _ in mismatches], ipa)
            found += len(mismatches)

        if action == "fix":
            logger.info(f"{found} dataset uuids fixed")
        else:
            logger.info(f"{found} dataset uuids without their group iPA prefix")
            if found:
                raise CommandError("Some dataset uuids lack their group iPA prefix: run 'rndt_uuids fix'")
