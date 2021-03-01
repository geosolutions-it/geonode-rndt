from django.conf.urls import url
from geonode.layers.urls import urlpatterns
from rndt.catalogue.views import csw_dispatcher

urlpatterns.insert(
    0, url(r"^csw/(?P<pa_name>[^/]*)/$", csw_dispatcher, name="csw_dispatcher")
)
