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

    urlpatterns += [
        url(r"^", include("rndt.api.urls")),
        url(r'^catalogue/', include('rndt.catalogue.urls')),
        url(r"^layers/", include("rndt.layers.urls")),
    ]
