import re

from django import forms

from haystack.forms import ModelSearchForm


BOOLEAN_OPERATORS = (
    ('&&', 'AND'),
    ('||', 'OR'),
)

FILTERS = (
    ('begins_with', 'Begins with'),
    ('ends_with', 'Ends with'),
    ('contains', 'Contains'),
    ('exactly_equals', 'Exactly equals'),
    ('regex', 'Regular expression'),
)

FILTERS_DICT = {
    'begins_with': '__istartswith',
    'ends_with': '__iendswith',
    'contains': '__icontains',
    'exactly_equals': '',
    'regex': '__iregex',
}

FILTERABLE_FIELDS = (
    ('headword', 'Headword'),
)


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

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['filter'] == 'regex':
            qs = cleaned_data['query_string']
            try:
                re.compile(qs)
            except Exception:
                self.add_error('query_string', forms.ValidationError('Invalid regular expression.'))


LexicalSearchFilterFormset = forms.formset_factory(LexicalSearchFilterForm)
