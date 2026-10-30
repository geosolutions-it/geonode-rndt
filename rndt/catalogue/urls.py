from django.urls import re_path

from rndt.catalogue.views import csw_dispatcher


urlpatterns = [
    re_path(r"^csw/(?P<pa_code>[^/]+)$", csw_dispatcher, name="rndt_csw_dispatcher"),
]
