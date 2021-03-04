from django.conf import settings

from rndt.layers.forms import LayerRNDTForm


def rndt_tags(request):
    return {
        "LayerRNDTForm": LayerRNDTForm
    }
