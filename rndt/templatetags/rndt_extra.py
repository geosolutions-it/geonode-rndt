from django import template
from geonode.base.models import ThesaurusKeyword
from geonode.layers.models import Layer
from rndt.models import LayerRNDT

register = template.Library()


@register.filter
def get_access_contraints(constraint_id, layer_id):
    if constraint_id in ["", "freetext"]:
        return False
    contraints_saved = LayerRNDT.objects.filter(layer=layer_id).exists()
    if not contraints_saved:
        return False
    contraints_saved = LayerRNDT.objects.get(layer=layer_id)
    keyword = ThesaurusKeyword.objects.get(id=constraint_id)
    return keyword.about in contraints_saved.constraints_other


@register.filter
def get_other_constraint(constraint_id, layer_id):
    if constraint_id in ["", "freetext"]:
        return False
    keyword = ThesaurusKeyword.objects.get(id=constraint_id)
    other_constraint = Layer.objects.get(id=layer_id).constraints_other
    return keyword.about in (other_constraint or [])


@register.filter
def get_resolution_value(value, layer_id):
    layer = LayerRNDT.objects.filter(layer=layer_id)
    if layer.exists():
        value.initial = layer.get().resolution
        return value
