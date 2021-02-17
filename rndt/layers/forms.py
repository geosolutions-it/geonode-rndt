from django import forms
from django.conf import settings
from django.forms import models
from django.utils.translation import ugettext_lazy as _
from geonode.base.models import ThesaurusKeywordLabel


class LayerRNDTForm(forms.Form):

    class Meta:
        fields = ['limitation_public_access', 'condition', 'free_text']

    lang = 'en' if not hasattr(settings, 'THESAURUS_DEFAULT_LANG') else settings.THESAURUS_DEFAULT_LANG

    limitation_public_access = models.ModelChoiceField(
            label=_('LimitationsOnPublicAccess'),
            required=False,
            queryset=ThesaurusKeywordLabel.objects.filter(keyword__thesaurus__identifier="LimitationsOnPublicAccess").filter(lang=lang),
        )

    condition = models.ModelChoiceField(
            label=_('ConditionsApplyingToAccessAndUse choices'),
            required=False,
            queryset=ThesaurusKeywordLabel.objects.filter(keyword__thesaurus__identifier="ConditionsApplyingToAccessAndUse").filter(lang=lang),
        )

    free_text = forms.CharField(
        label=_('ConditionsApplyingToAccessAndUse free text'),
        widget=forms.Textarea,
        required=False)
