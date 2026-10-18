from django import forms

from .models import Rubrique


class NoteRapideForm(forms.Form):
    texte = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), strip=True,
                            error_messages={"required": "Écrivez au moins une phrase."})
    latitude = forms.FloatField(required=False, min_value=-90, max_value=90, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, min_value=-180, max_value=180, widget=forms.HiddenInput)
    rubriques = forms.ModelMultipleChoiceField(queryset=Rubrique.objects.none(), required=False,
                                               widget=forms.CheckboxSelectMultiple, label="Étiquettes")

    def __init__(self, *args, stage, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rubriques"].queryset = Rubrique.pour_stage(stage)
