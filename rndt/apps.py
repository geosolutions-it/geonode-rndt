import os

from django.apps import AppConfig
from django.conf import settings


class RndtConfig(AppConfig):
    name = "rndt"

    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(RndtConfig, self).ready()


def run_setup_hooks(*args, **kwargs):
    from django.conf.urls import include, url
    from geonode.urls import urlpatterns

    LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(LOCAL_ROOT, "templates"))

    settings.TEMPLATES[0]["OPTIONS"]["context_processors"].append(
        "rndt.context_processors.rndt_tags"
    )

    rndt_exclude_fields = ['constraints_other', 'restriction_code_type']
    if hasattr(settings, 'ADVANCED_EDIT_EXCLUDE_FIELD'):
        settings.ADVANCED_EDIT_EXCLUDE_FIELD += rndt_exclude_fields
    else:
        setattr(settings, 'ADVANCED_EDIT_EXCLUDE_FIELD', rndt_exclude_fields)

    rdt_parsers = ['__DEFAULT__', 'rndt.layers.metadata.rndt_parser']
    if not getattr(settings, 'METADATA_PARSERS', None):
        setattr(settings, 'METADATA_PARSERS', rdt_parsers)
    elif 'rndt.layers.metadata.rndt_parser' not in settings.METADATA_PARSERS:
        settings.METADATA_PARSERS.extend(["rndt.layers.metadata.rndt_parser"])
        setattr(settings, "METADATA_PARSERS", settings.METADATA_PARSERS)

    rndt_storers = ['rndt.layers.storer.rndt_storer']
    if not getattr(settings, 'METADATA_STORERS', None):
        setattr(settings, 'METADATA_STORERS', rndt_storers)
    elif rndt_storers[0] not in settings.METADATA_STORERS:
        settings.METADATA_STORERS.extend(rndt_storers)
        setattr(settings, "METADATA_STORERS", settings.METADATA_STORERS)

    rndt_required_fields = ['id_access_contraints', 'id_use_constraints', 'id_resolution', 'id_accuracy']
    if not hasattr(settings, 'UI_DEFAULT_MANDATORY_FIELDS'):
        setattr(settings, 'UI_DEFAULT_MANDATORY_FIELDS', rndt_required_fields)
    else:
        settings.UI_DEFAULT_MANDATORY_FIELDS.extend(rndt_required_fields)
        setattr(settings, 'UI_DEFAULT_MANDATORY_FIELDS', settings.UI_DEFAULT_MANDATORY_FIELDS)


    urlpatterns += [
        url(r"^", include("rndt.api.urls")),
        url(r'^catalogue/', include('rndt.catalogue.urls')),
        url(r"^datasets/", include("rndt.layers.urls")),
    ]
