from django.conf.urls import url
from geonode.layers.urls import urlpatterns
from rndt.layers.views import layer_metadata

urlpatterns.insert(0, url(r"^(?P<layername>[^/]*)/metadata$", layer_metadata, name="layer_metadata"))
