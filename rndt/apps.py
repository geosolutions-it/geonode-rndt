import os

from django.apps import AppConfig
from django.conf import settings


class RndtConfig(AppConfig):
    name = "rndt"

    def ready(self):
        super(RndtConfig, self).ready()

        """Finalize setup"""
        run_setup_hooks()

        from rndt.metadata.handler import init as metadata_init
        metadata_init()



def run_setup_hooks(*args, **kwargs):
    from django.conf.urls import include
    from django.urls import re_path
    from geonode.urls import urlpatterns

    LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(LOCAL_ROOT, "templates"))

    # settings.TEMPLATES[0]["OPTIONS"]["context_processors"].append("rndt.context_processors.rndt_tags")

    RNDT_PARSER_FUNCTION = "rndt.metadata.parser.rndt_parser"

    rndt_parsers = ["__DEFAULT__", RNDT_PARSER_FUNCTION]
    if not getattr(settings, "METADATA_PARSERS", None):
        setattr(settings, "METADATA_PARSERS", rndt_parsers)
    elif RNDT_PARSER_FUNCTION not in settings.METADATA_PARSERS:
        settings.METADATA_PARSERS.extend([RNDT_PARSER_FUNCTION])
        setattr(settings, "METADATA_PARSERS", settings.METADATA_PARSERS)

    urlpatterns += [
        re_path(r"^", include("rndt.api.urls")),
        re_path(r"^catalogue/", include("rndt.catalogue.urls")),
        # re_path(r"^datasets/", include("rndt.layers.urls")),
    ]
