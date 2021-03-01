
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponse
from geonode.catalogue.backends.pycsw_local import CONFIGURATION
from geonode.catalogue.views import CswGlobalDispatcher
from pycsw import server


def csw_dispatcher(request, pa_name):    
    if settings.CATALOGUE['default']['ENGINE'] != 'geonode.catalogue.backends.pycsw_local':
        return HttpResponseRedirect(settings.CATALOGUE['default']['URL'])

    dispatcher = RndtCswDispatcher(request)

    mdict = dispatcher.get_configurations()
    env = dispatcher.define_env_data()

    # Save original filter before doing anything
    mdict_filter = mdict['repository']['filter']

    try:
        # Filter out Layers not accessible to the User
        mdict = dispatcher.get_authorized_layer_ids()

        csw = server.Csw(mdict, env, version='2.0.2')

        content = dispatcher.get_xml_tree(csw)
    finally:
        # Restore original filter before doing anything
        mdict['repository']['filter'] = mdict_filter

    return HttpResponse(content, content_type=csw.contenttype)


class RndtCswDispatcher(CswGlobalDispatcher):
    def __init__(self, request):
        super().__init__(request)
        # CONFIGURATION['repository']['filter'] = f"uuid like 'ipa5%'"
        self.mdict = dict(settings.PYCSW['CONFIGURATION'], **CONFIGURATION)
