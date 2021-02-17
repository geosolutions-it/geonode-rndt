from geonode.layers.views import check_keyword_write_perms
from geonode.layers.views import layer_metadata as geonode_layer_view
from geonode.layers.views import login_required


@login_required
@check_keyword_write_perms
def layer_metadata(
        request,
        layername,
        template='layers/layer_metadata.html',
        ajax=True, *args, **kwargs
    ):
    print("using custom view")
    return geonode_layer_view(request,layername, template, ajax, *args, **kwargs)
