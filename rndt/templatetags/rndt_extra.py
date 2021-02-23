from django import template
from geonode.base.models import ThesaurusKeywordLabel
from geonode.layers.models import Layer
from rndt.models import LayerRNDT

register = template.Library()

@register.filter
def is_saved_one(constraint_id, layer_id):
    if constraint_id in ['', 'freetext']:
        return False
    contraints_saved = LayerRNDT.objects.filter(layer=layer_id).exists()
    if not contraints_saved:
        return False
    contraints_saved = LayerRNDT.objects.get(layer=layer_id)
    label = ThesaurusKeywordLabel.objects.get(id=constraint_id)
    return label.label in contraints_saved.constraints_other

@register.filter
def get_other_constraint(constraint_id, layer_id):
    if constraint_id in ['', 'freetext']:
        return False
    label = ThesaurusKeywordLabel.objects.get(id=constraint_id)
    other_constraint = Layer.objects.get(id=layer_id).constraints_other
    return label.label in (other_constraint or [])
