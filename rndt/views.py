from django.http.response import HttpResponse
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from rndt.models import PubblicaAmministrazione


class PubblicaAmministrazioneResource(ModelResource):
    """Tags api"""

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'pubblica_amministrazione'

        return super(PubblicaAmministrazioneResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = PubblicaAmministrazione.objects.all().order_by('ipa')
        resource_name = 'pubblica_amministrazione'
        allowed_methods = ['get']
        filtering = {
            'ipa': ALL,
            'name': ALL
        }
