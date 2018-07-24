import re

from django import forms
from django.utils.translation import gettext as _

from haystack.forms import ModelSearchForm


BOOLEAN_OPERATORS = (
    ('and', 'y'),
    ('or', 'o'),
    ('and_n', 'y no'),
    ('or_n', 'o no'),
)

FILTERS = (
    ('begins_with', _('Empieza con')),
    ('ends_with', _('Termina con')),
    ('contains', _('Incluye')),
    ('exactly_equals', _('Es exactamente igual a')),
    ('regex', _('Expresión regular')),
)

FILTERS_DICT = {
    'begins_with': '__istartswith',
    'ends_with': '__iendswith',
    'contains': '__icontains',
    'exactly_equals': '',
    'regex': '__iregex',
}

FILTERABLE_FIELDS = (
    ('headword', _('Entrada')),
)

FILTERABLE_FIELDS_DICT = {
    'headword': 'headword',
}


class LexiconSearchForm(ModelSearchForm):
    q = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mr-3'}))


class LexicalSearchFilterForm(forms.Form):
    query_string = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    operator = forms.ChoiceField(
        choices=BOOLEAN_OPERATORS,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )
    filter = forms.ChoiceField(
        choices=FILTERS,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )
    filter_on = forms.ChoiceField(
        choices=FILTERABLE_FIELDS,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )
    vln = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['filter'] == 'regex':
            qs = cleaned_data['query_string']
            try:
                re.compile(qs)
            except Exception:
                self.add_error('query_string', forms.ValidationError(_('Expresión regular no válida.')))


LexicalSearchFilterFormset = forms.formset_factory(LexicalSearchFilterForm)
