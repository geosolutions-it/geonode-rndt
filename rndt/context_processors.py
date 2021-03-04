from django.conf import settings

from rndt.layers.forms import LayerRNDTForm


def rndt_tags(request):
    return {
        "LayerRNDTForm": LayerRNDTForm,
        "REQUIRED_RNDT_FIELDS": settings.REQUIRED_RNDT_FIELDS if hasattr(settings, 'REQUIRED_RNDT_FIELDS') else []
    }
