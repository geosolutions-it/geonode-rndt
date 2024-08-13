from django.conf.urls import include
from django.urls import re_path
from geonode.api.urls import api
from rndt.views import PubblicaAmministrazioneResource

api.register(PubblicaAmministrazioneResource())

pubblica_amministrazione = PubblicaAmministrazioneResource()

urlpatterns = [re_path(r"^(?P<api_name>api)/", include(pubblica_amministrazione.urls), name="pubblica_amministrazione")]
