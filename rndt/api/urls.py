from django.urls import include, re_path
from geonode.api.urls import api

from rndt.views import PubblicaAmministrazioneResource


pubblica_amministrazione = PubblicaAmministrazioneResource()
api.register(pubblica_amministrazione)  # only lists it in /api/: GeoNode's api.urls are already built
urlpatterns = [re_path(r"^(?P<api_name>api)/", include(pubblica_amministrazione.urls))]
