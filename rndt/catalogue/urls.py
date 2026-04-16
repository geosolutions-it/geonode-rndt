from django.urls import re_path

from rndt.catalogue.views import csw_dispatcher


def add_rndt_csw_dispatcher():
    from geonode.catalogue.urls import urlpatterns as csw_patterns
    csw_patterns.insert(0, re_path(r"^csw/(?P<pa_code>[^/]+)$", csw_dispatcher, name="rndt_csw_dispatcher"))
