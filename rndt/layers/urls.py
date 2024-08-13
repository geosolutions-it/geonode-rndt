from django.urls import re_path
from geonode.layers.urls import urlpatterns
from rndt.layers.views import layer_metadata

urlpatterns.insert(0, re_path(r"^(?P<layername>[^/]*)/metadata$", layer_metadata, name="layer_metadata"))
