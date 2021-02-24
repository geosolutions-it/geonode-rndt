from django import forms
from django.conf import settings
from django.forms import models
from django.forms.widgets import NumberInput
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from geonode.base.models import ThesaurusKeyword, ThesaurusKeywordLabel


class LayerRNDTForm(forms.Form):
    class Meta:
        fields = ["access_contraints", "use_constraints", "free_text", "resolution"]

    access_contraints = forms.ChoiceField(
        label=_("LimitationsOnPublicAccess"),
        required=False
    )

    use_constraints = forms.ChoiceField(
        label=_("ConditionsApplyingToAccessAndUse choices"), required=False
    )

    free_text = forms.CharField(
        label=_("ConditionsApplyingToAccessAndUse free text"),
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=False,
    )

    resolution = forms.FloatField(
        label=_("resolution choices"),
        required=False,
        widget=NumberInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super(LayerRNDTForm, self).__init__(*args, *kwargs)
        lang = get_language()

        # getting the default choices from the thesaurus
        choices_usability = self._get_thesauro_keyword_label('ConditionsApplyingToAccessAndUse', lang)
        choices_contraints = self._get_thesauro_keyword_label('LimitationsOnPublicAccess', lang)
        # adding custom choices in order to let the free-text textarea appear when selected
        default_choices = [
            ("", "---------"),
            *choices_usability,
            ("freetext", "Free text"),
        ]

        self.fields["use_constraints"].choices = default_choices
        self.fields["access_contraints"].choices = [
            ("", "---------"), 
            *choices_contraints
        ]

    @staticmethod
    def _get_thesauro_keyword_label(identifier, lang):
        qs_local = []
        qs_non_local = []
        for key in ThesaurusKeyword.objects.filter(thesaurus__identifier=identifier):
            label = ThesaurusKeywordLabel.objects.filter(keyword=key).filter(lang=lang)
            if label.exists():
                qs_local.append((label.get().keyword.id, label.get().label))
            else:
                qs_non_local.append((key.id, key.alt_label))

        return qs_non_local + qs_local
