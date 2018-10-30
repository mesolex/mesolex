import re

from django import forms
from django.utils.translation import gettext as _


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
    ('lemma', _('Entrada')),
    ('gloss', _('Glosa')),
    ('root', _('Raiz')),
    ('category', _('Campo semántico')),
    ('part_of_speech', _('Categoría gramatical')),
    ('inflectional_type', _('Inflexión')),
)

FILTERABLE_FIELDS_DICT = {
    'lemma': ('lemma', 'variant__value'),
    'gloss': ('gloss__value', ),
    'root': ('root__value', ),
    'category': ('category__value', ),
    'part_of_speech': ('grammargroup__part_of_speech', ),
    'inflectional_type': ('grammargroup__inflectional_type', ),
}


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
        if 'filter' in cleaned_data and cleaned_data['filter'] == 'regex':
            qs = cleaned_data['query_string']
            try:
                re.compile(qs)
            except Exception:
                self.add_error('query_string', forms.ValidationError(_('Expresión regular no válida.')))


LexicalSearchFilterFormset = forms.formset_factory(LexicalSearchFilterForm)
