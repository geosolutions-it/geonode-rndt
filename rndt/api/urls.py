from django.conf.urls import include, url
from rndt.views import PubblicaAmministrazioneResource
from geonode.api.urls import api

api.register(PubblicaAmministrazioneResource())

x = PubblicaAmministrazioneResource()

urlpatterns = [
    url(r'^(?P<api_name>api)/', include(x.urls), name="pubblica_amministrazione"),
]
