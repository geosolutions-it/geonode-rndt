import json
from django.db import migrations
from geonode.metadata.models import SparseField


def migrate_layerrndt_to_sparse(apps, schema_editor):
    """
    Create RNDT SparseField from previous model
    """
    LayerRNDT_model = apps.get_model("rndt", "LayerRNDT")
    ResourceBase_model = apps.get_model("base", "ResourceBase")
    SparseField_model = apps.get_model("metadata", "SparseField")

    for lrndt in LayerRNDT_model.objects.all():
        rbase = ResourceBase_model.objects.get(pk=lrndt.layer_id)

        for field, sparsename in (
                ("resolution", "rndt_resolution"),
                ("accuracy", "rndt_accuracy"),
        ):
            value = getattr(lrndt, field)
            if value is not None:
                SparseField_model.objects.get_or_create(
                    defaults={"value":value},
                    resource=rbase,
                    name=sparsename)

        if constr_use:=lrndt.layer.constraints_other:
            if constr_use not in ("None",):  # avoid some old model issues
                is_url = constr_use.startswith(
                        "http://inspire.ec.europa.eu/metadata-codelist/ConditionsApplyingToAccessAndUse")
                sparseval = {
                    "inspire_url": is_url,
                    "url" if is_url else "freetext": constr_use}
                SparseField_model.objects.get_or_create(
                        defaults={"value": json.dumps(sparseval)},
                        resource=rbase,
                        name="rndt_ConditionsApplyingToAccessAndUse")

        if limit_access:=lrndt.constraints_other:
            limit_val = {
                "id": limit_access,
                "label": limit_access.split("/")[-1]
            }
            SparseField_model.objects.get_or_create(
                    defaults={"value": json.dumps(limit_val)},
                    resource=rbase,
                    name="rndt_LimitationsOnPublicAccess")


class Migration(migrations.Migration):

    dependencies = [
        ("rndt", "0006_layerrndt"),
        ("metadata", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_layerrndt_to_sparse, migrations.RunPython.noop),
    ]
