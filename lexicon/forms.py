from django import forms

from haystack.forms import ModelSearchForm


BOOLEAN_OPERATORS = (
    ('&&', 'AND'),
    ('||', 'OR'),
)

FILTERS = (
    ('__istartswith', 'Begins with'),
    ('__iendswith', 'Ends with'),
    ('__icontains', 'Contains'),
    ('__isexactly', 'Exactly equals'),
)

FILTERABLE_FIELDS = (
    ('headword', 'Headword'),
)


class LexiconSearchForm(ModelSearchForm):
    q = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mr-3'}))


class LexicalSearchFilterForm(forms.Form):
    query_string = forms.CharField()
    operator = forms.ChoiceField(
        choices=BOOLEAN_OPERATORS,
    )
    filter = forms.ChoiceField(
        choices=FILTERS,
    )
    filter_on = forms.ChoiceField(
        choices=FILTERABLE_FIELDS,
    )


LexicalSearchFilterFormset = forms.formset_factory(LexicalSearchFilterForm)
