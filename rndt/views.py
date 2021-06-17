import json
import time

from django.core.serializers.json import DjangoJSONEncoder
from geonode.api.api import  TypeFilteredResource
from geonode.api.authorization import (ApiLockdownAuthorization,)
from geonode.base.models import ResourceBase
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer

from rndt.models import PubblicaAmministrazione


class PACountJSONSerializer(Serializer):

    def get_resources_counts(self, options):
        counts = dict()
        for pa in PubblicaAmministrazione.objects.all():
            resources = ResourceBase.objects.filter(group__groupprofile__groupprofilerndt__pa__ipa=pa.ipa)
            if options.get('resource_type_filter', None) is not None:
                resources = resources.filter(resource_type=options.get('resource_type_filter'))
            counts[pa.id] = resources.count()
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

        if request.GET.get('type', None) is not None:
            options['resource_type_filter'] = request.GET.get('type')

        return super(PubblicaAmministrazioneResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = PubblicaAmministrazione.objects.all().order_by('ipa')
        resource_name = 'pubblica_amministrazione'
        allowed_methods = ['get']
        filtering = {
            'ipa': ALL_WITH_RELATIONS,
            'name': ALL
        }
        serializer = PACountJSONSerializer()
        authorization = ApiLockdownAuthorization()
