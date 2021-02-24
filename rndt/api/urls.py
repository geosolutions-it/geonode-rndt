from django.conf.urls import include, url
from geonode.api.urls import api
from rndt.views import PubblicaAmministrazioneResource

api.register(PubblicaAmministrazioneResource())

pubblica_amministrazione = PubblicaAmministrazioneResource()

urlpatterns = [
    url(r'^(?P<api_name>api)/', include(pubblica_amministrazione.urls), name="pubblica_amministrazione")
]
