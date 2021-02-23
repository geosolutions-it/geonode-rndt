from django import forms
from django.conf import settings
from django.forms import models
from django.forms.widgets import NumberInput
from django.utils.translation import ugettext_lazy as _
from geonode.base.models import ThesaurusKeywordLabel


class LayerRNDTForm(forms.Form):
    class Meta:
        fields = ["access_contraints", "use_constraints", "free_text"]

    lang = (
        "en"
        if not hasattr(settings, "THESAURUS_DEFAULT_LANG")
        else settings.THESAURUS_DEFAULT_LANG
    )

    access_contraints = models.ModelChoiceField(
        label=_("LimitationsOnPublicAccess"),
        required=False,
        queryset=ThesaurusKeywordLabel.objects.filter(
            keyword__thesaurus__identifier="LimitationsOnPublicAccess"
        ).filter(lang=lang),
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
        lang = (
            "en"
            if not hasattr(settings, "THESAURUS_DEFAULT_LANG")
            else settings.THESAURUS_DEFAULT_LANG
        )
        # getting the default choices from the thesaurus
        choices_usability = ThesaurusKeywordLabel.objects.filter(
            keyword__thesaurus__identifier="ConditionsApplyingToAccessAndUse"
        ).filter(lang=lang)

        choices_as_tuple = [(x.id, x.label) for x in choices_usability]
        # adding custom choices in order to let the free-text textarea appear when selected
        default_choices = [
            ("", "---------"),
            *choices_as_tuple,
            ("freetext", "Free text"),
        ]

        self.fields["use_constraints"].choices = default_choices
