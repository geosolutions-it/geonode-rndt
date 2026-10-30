import json
from importlib import import_module

from django.db import migrations

m0007 = import_module("rndt.migrations.0007_migrate_metadata")


def restore_constraints_other(apps):
    """The 5.0 handler saved "Missing value" in ResourceBase.constraints_other: restore it from the SparseField"""
    ResourceBase_model = apps.get_model("base", "ResourceBase")
    SparseField_model = apps.get_model("metadata", "SparseField")

    sparsefields = SparseField_model.objects.filter(
        name="rndt_ConditionsApplyingToAccessAndUse", resource__constraints_other="Missing value"
    )
    for sparse in sparsefields.iterator():
        try:
            conditions = json.loads(sparse.value or "{}")
        except ValueError:
            continue
        val = conditions.get("url") if conditions.get("inspire_url", False) else conditions.get("freetext")
        if val and val.strip():
            ResourceBase_model.objects.filter(pk=sparse.resource_id).update(constraints_other=val.strip())


def fix_access_labels(apps):
    """The 0007 migration used the URI tail as the label"""
    SparseField_model = apps.get_model("metadata", "SparseField")
    labels = {}  # few distinct URIs, many resources

    for sparse in SparseField_model.objects.filter(name="rndt_LimitationsOnPublicAccess").iterator():
        try:
            limit_val = json.loads(sparse.value or "{}")
        except ValueError:
            continue
        about = limit_val.get("id")
        if about and limit_val.get("label") == about.rstrip("/").split("/")[-1]:
            if about not in labels:
                labels[about] = m0007.keyword_label(apps, about)
            label = labels[about]
            if label != limit_val["label"]:
                limit_val["label"] = label
                sparse.value = json.dumps(limit_val)
                sparse.save(update_fields=["value"])


def fix_migrated_metadata(apps, schema_editor):
    # before migrate_use_conditions, which skips the "Missing value" resources
    restore_constraints_other(apps)
    # the resources skipped by the previous 0007 migration
    m0007.migrate_use_conditions(apps)
    fix_access_labels(apps)


class Migration(migrations.Migration):

    dependencies = [
        ("rndt", "0008_delete_layerrndt"),
    ]

    operations = [
        migrations.RunPython(fix_migrated_metadata, migrations.RunPython.noop),
    ]
