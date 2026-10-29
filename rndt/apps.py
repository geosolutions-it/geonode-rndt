import os

from django.apps import AppConfig
from django.conf import settings


class RndtConfig(AppConfig):
    name = "rndt"

    def ready(self):
        super(RndtConfig, self).ready()

        """Finalize setup"""
        run_setup_hooks()

        from rndt import checks  # noqa: F401
        from rndt.metadata.handler import init as metadata_init

        metadata_init()


def run_setup_hooks(*args, **kwargs):
    inject_urls()

    LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(LOCAL_ROOT, "templates"))

    RNDT_PARSER_FUNCTION = "rndt.metadata.parser.rndt_parser"

    parsers = list(getattr(settings, "METADATA_PARSERS", None) or ["__DEFAULT__"])
    if RNDT_PARSER_FUNCTION not in parsers:
        parsers.append(RNDT_PARSER_FUNCTION)
    settings.METADATA_PARSERS = parsers


def is_rndt_urls(pattern):
    return getattr(getattr(pattern, "urlconf_name", None), "__name__", None) == "rndt.urls"


def inject_urls():
    """Add rndt.urls to the GeoNode ones, once"""
    from django.urls import include, re_path
    from geonode.urls import urlpatterns

    if not any(is_rndt_urls(p) for p in urlpatterns):
        urlpatterns.insert(0, re_path(r"", include("rndt.urls")))
