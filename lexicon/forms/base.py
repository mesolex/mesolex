from django import forms
from django.db.models import Q

from lexicon.models import Entry
from mesolex.config import LANGUAGES
from query_builder.forms import QueryBuilderGlobalFiltersForm


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)
    dataset = forms.ChoiceField(
        choices=[(l['code'], l['label']) for l in LANGUAGES.values()],
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        if only_with_sound:
            return Entry.objects.filter(media__isnull=(not only_with_sound))

        return Entry.objects.all()

    def clean_dataset(self):
        dataset = self.cleaned_data['dataset']
        if dataset:
            return Entry.objects.filter(language=dataset)

        return Entry.objects.all()
