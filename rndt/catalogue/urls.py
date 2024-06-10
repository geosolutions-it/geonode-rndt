
from django.urls import re_path
from geonode.layers.urls import urlpatterns
from rndt.catalogue.views import csw_dispatcher

urlpatterns.insert(
    0, re_path(r"^csw/(?P<pa_code>[^/]*)/$", csw_dispatcher, name="csw_dispatcher")
)
