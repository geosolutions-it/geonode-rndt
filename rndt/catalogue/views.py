
from geonode.catalogue.views import csw_global_dispatch


def csw_dispatcher(request, pa_code):    
    return csw_global_dispatch(request, LayerFilters(pa_code).filter_layers)

class LayerFilters():
    def __init__(self, pa_code):
        self.pa_code = pa_code
    def filter_layers(self, layers):
        return layers.filter(uuid__startswith=self.pa_code)
