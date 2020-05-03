from django import forms
from django.db.models import Q

from query_builder.forms import QueryBuilderGlobalFiltersForm

from mesolex.config import LANGUAGES


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)
    dataset = forms.ChoiceField(
        choices=[(l['code'], l['label']) for l in LANGUAGES.values()],
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        if only_with_sound:
            return Q(media__isnull=(not only_with_sound))
        return Q()
      
    def clean_dataset(self):
        dataset = self.cleaned_data['dataset']
        if dataset:
            return Q(language=dataset)
        return Q()

