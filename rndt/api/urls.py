from django.conf.urls import include, url
from rndt.views import PubblicaAmministrazioneResource
from geonode.api.urls import api

api.register(PubblicaAmministrazioneResource())

pubblica_amministrazione = PubblicaAmministrazioneResource()

urlpatterns = [
<<<<<<< HEAD
    url(r'^(?P<api_name>api)/', include(pubblica_amministrazione.urls), name="pubblica_amministrazione")
=======
    url(r'^(?P<api_name>api)/', include(pubblica_amministrazione.urls), name="pubblica_amministrazione"),
>>>>>>> 259f4621cfab7aec9765974c8cd4c6e8d5e17741
]
