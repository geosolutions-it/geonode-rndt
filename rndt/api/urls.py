from django.conf.urls import include, url
from rndt.views import PubblicaAmministrazioneResource
from geonode.api.urls import api

api.register(PubblicaAmministrazioneResource())

pubblica_amministrazione = PubblicaAmministrazioneResource()

urlpatterns = [
    url(r'^(?P<api_name>api)/', include(pubblica_amministrazione.urls), name="pubblica_amministrazione"),
]
