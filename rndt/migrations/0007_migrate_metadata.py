import json
from django.db import migrations

CONDITIONS_URL = "http://inspire.ec.europa.eu/metadata-codelist/ConditionsApplyingToAccessAndUse"


def keyword_label(apps, about):
    """Label of the thesaurus keyword, as in rndt_get_keyword_label_by_about; the URI tail if not loaded yet"""
    keyword = apps.get_model("base", "ThesaurusKeyword").objects.filter(about=about).first()
    if keyword:
        labels = apps.get_model("base", "ThesaurusKeywordLabel").objects.filter(keyword=keyword)
        for lang in ("it", "en"):
            label = labels.filter(lang=lang).first()
            if label:
                return label.label
        if keyword.alt_label:
            return keyword.alt_label
    return about.rstrip("/").split("/")[-1]


def migrate_use_conditions(apps):
    """Create the use conditions SparseField from ResourceBase.constraints_other, for all the resources"""
    ResourceBase_model = apps.get_model("base", "ResourceBase")
    SparseField_model = apps.get_model("metadata", "SparseField")

    resources = ResourceBase_model.objects.exclude(constraints_other__isnull=True)
    for rbase in resources.only("id", "constraints_other").iterator():
        constr_use = rbase.constraints_other.strip()
        if constr_use in ("", "None", "Missing value"):  # old model issues, and the 5.0 handler placeholder
            continue
        is_url = constr_use.startswith(CONDITIONS_URL)
        sparseval = {"inspire_url": is_url, "url" if is_url else "freetext": constr_use}
        SparseField_model.objects.get_or_create(
            defaults={"value": json.dumps(sparseval)},
            resource_id=rbase.id,
            name="rndt_ConditionsApplyingToAccessAndUse",
        )


def migrate_layerrndt_to_sparse(apps, schema_editor):
    """
    Create RNDT SparseField from previous model
    """
    LayerRNDT_model = apps.get_model("rndt", "LayerRNDT")
    SparseField_model = apps.get_model("metadata", "SparseField")
    labels = {}  # few distinct URIs, many layers

    for lrndt in LayerRNDT_model.objects.all():
        for field, sparsename in (
            ("resolution", "rndt_resolution"),
            ("accuracy", "rndt_accuracy"),
        ):
            value = getattr(lrndt, field)
            if value is not None:
                SparseField_model.objects.get_or_create(
                    defaults={"value": str(value)}, resource_id=lrndt.layer_id, name=sparsename
                )

        if limit_access := (lrndt.constraints_other or "").strip():
            if limit_access != "None":
                if limit_access not in labels:
                    labels[limit_access] = keyword_label(apps, limit_access)
                limit_val = {"id": limit_access, "label": labels[limit_access]}
                SparseField_model.objects.get_or_create(
                    defaults={"value": json.dumps(limit_val)},
                    resource_id=lrndt.layer_id,
                    name="rndt_LimitationsOnPublicAccess",
                )

    # the use conditions are in ResourceBase: also for the resources without a LayerRNDT
    migrate_use_conditions(apps)


class Migration(migrations.Migration):

    dependencies = [
        ("rndt", "0006_layerrndt"),
        ("metadata", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_layerrndt_to_sparse, migrations.RunPython.noop),
    ]
