import json
import re

from django.http import HttpResponse
from geonode.layers.views import (_PERMISSION_MSG_METADATA, _resolve_layer,
                                  check_keyword_write_perms)
from geonode.layers.views import layer_metadata as geonode_layer_view
from geonode.layers.views import logger, login_required
from rndt.layers.forms import LayerRNDTForm
from rndt.models import LayerRNDT


@login_required
@check_keyword_write_perms
def layer_metadata(
        request,
        layername,
        template='layers/layer_metadata.html',
        ajax=True, *args, **kwargs
    ):
    if request.method == "POST":
        layer = _resolve_layer(
            request,
            layername,
            'base.change_resourcebase_metadata',
            _PERMISSION_MSG_METADATA)
        constraint_form = LayerRNDTForm(request.POST)
        if not constraint_form.is_valid():
            logger.error(f"Additional Contraints form is not valid: {constraint_form.errors}")
            out = {
                'success': False,
                'errors': [
                    re.sub(re.compile('<.*?>'), '', str(err)) for err in constraint_form.errors]
            }
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=400)

        constraint_form.cleaned_data
        items = constraint_form.cleaned_data
        for v in items.values():
            x = LayerRNDT(
                layer=layer,
                constraints_other=v
            )
            x.save()
    
    return geonode_layer_view(request, layername, template, ajax, *args, **kwargs)
