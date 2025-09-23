from django import template
from django.core.validators import URLValidator
from geonode.base.models import Thesaurus, ThesaurusKeyword, ThesaurusKeywordLabel
from rndt.models import LayerRNDT

register = template.Library()


@register.filter
def get_thesaurus_about(thesaurus_id):
    t = Thesaurus.objects.filter(id=thesaurus_id)
    if t.exists():
        return Thesaurus.objects.get(id=thesaurus_id).about


@register.filter
def rndt_get_localized_tkeyword(tkeyword: ThesaurusKeyword):
    for lang in ("it", "en"):
        t = ThesaurusKeywordLabel.objects.filter(keyword=tkeyword, lang=lang)
        if t.exists():
            return t.first().label

    return tkeyword.alt_label


@register.filter
def rndt_get_keyword_label_by_about(about):
    tk = ThesaurusKeyword.objects.filter(about=about).first()
    if tk:
        for lang in ("it", "en"):
            tkl = ThesaurusKeywordLabel.objects.filter(keyword=tk, lang=lang)
            if tkl.exists():
                return tkl.first().label
        return tk.alt_label
    return None

