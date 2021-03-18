import json
import time

from django.core.serializers.json import DjangoJSONEncoder
from geonode.api.api import TypeFilteredResource
from geonode.api.authorization import ApiLockdownAuthorization
from geonode.layers.models import Layer
from tastypie.constants import ALL
from tastypie.serializers import Serializer

from rndt.models import PubblicaAmministrazione


class PACountJSONSerializer(Serializer):

    def get_resources_counts(self, options):
        counts = dict()
        for pa in PubblicaAmministrazione.objects.all():
            layer_with_ipa = Layer.objects.filter(uuid__startswith=pa.ipa).count()
            counts[pa.id] = layer_with_ipa
        return counts

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        counts = self.get_resources_counts(options)
        if 'objects' in data:
            for item in data['objects']:
                item['count'] = counts.get(item['id'], 0)
        # Add in the current time.
        data['requested_time'] = time.time()

        return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)
class PubblicaAmministrazioneResource(TypeFilteredResource):
    """PA api"""

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'id'

        return super(PubblicaAmministrazioneResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = PubblicaAmministrazione.objects.all().order_by('ipa')
        resource_name = 'pubblica_amministrazione'
        allowed_methods = ['get']
        filtering = {
            'ipa': ALL,
            'name': ALL
        }
        serializer = PACountJSONSerializer()
        authorization = ApiLockdownAuthorization()
