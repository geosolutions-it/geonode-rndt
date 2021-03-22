from geonode.catalogue.views import csw_global_dispatch


def csw_dispatcher(request, pa_code):
    return csw_global_dispatch(
        request,
        layer_filter=LayerFilters(pa_code).filter_layers,
        config_updater=RndtCswConfigurer(pa_code).config_updater)


class LayerFilters:
    def __init__(self, pa_code):
        self.pa_code = pa_code

    def filter_layers(self, layers):
        return layers.filter(uuid__startswith=self.pa_code)


class RndtCswConfigurer:
    def __init__(self, pa_code):
        self.pa_code = pa_code

    def config_updater(self, d: dict) -> dict:
        old_url = d['server']['url']
        d['server']['url'] = f'{old_url}/{self.pa_code}'
        return d
