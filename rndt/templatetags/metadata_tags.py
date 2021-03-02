from django import template
from django.core.validators import URLValidator
from geonode.base.models import Thesaurus, ThesaurusKeyword
from rndt.models import LayerRNDT

register = template.Library()


@register.filter
def get_thesaurus_about(thesaurus_id):
    return Thesaurus.objects.get(id=thesaurus_id).about


@register.filter
def get_access_contraints_url(layer_id):
    x = LayerRNDT.objects.filter(layer_id=layer_id)
    if x.exists():
        return x.get().constraints_other
    return None


@register.filter
def get_access_contraints_keyword(layer_id):
    x = LayerRNDT.objects.filter(layer_id=layer_id)
    if x.exists():
        url = x.get().constraints_other
        return ThesaurusKeyword.objects.get(about=url).alt_label
    return None


@register.filter
def get_use_constraint_keyword(keyword_url):
    return ThesaurusKeyword.objects.get(about=keyword_url).alt_label


@register.filter
def is_url(item):
    try:
        validator = URLValidator()
        validator(item)
        return True
    except:
        return False


@register.filter
def get_spatial_resolution(layer_id):
    resolution = LayerRNDT.objects.filter(layer_id=layer_id)
    if resolution.exists():
        return LayerRNDT.objects.get(layer_id=layer_id).resolution
    return layer_id

@register.filter
def get_positional_accuracy(layer_id):
    accuracy = LayerRNDT.objects.filter(layer_id=layer_id)
    if accuracy.exists():
        return LayerRNDT.objects.get(layer_id=layer_id).accuracy
    return layer_id
