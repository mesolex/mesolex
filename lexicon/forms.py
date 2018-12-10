import json
import re

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .utils import (
    to_vln,
    ForceProxyEncoder,
)

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

# TODO: investigate why these gettext-strings have to be
# lazy to work as expected when serialized by the formset.
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

    def get_filter_action_and_query(self):
        """
        filter_arg_val is the type of filtering to perform in the query,
        e.g. "__istartswith" or "__iregex". Normally this will be
        whatever in FILTERS_DICT corresponds to the particular value
        from FILTERS. But if this has vowel length neutralization,
        it will be transformed from whatever it was into a specially
        constructed regular expression.
        """
        
        if not self.is_bound:
            return (None, None)
        
        form_data = self.cleaned_data
        filter_str = form_data['filter']
        if form_data['vln']:
            (filter_arg_val, query_string,) = to_vln(filter_str, form_data['query_string'])
        else:
            filter_arg_val = FILTERS_DICT.get(filter_str, '')
            query_string = form_data['query_string']
        
        return (filter_arg_val, query_string)

    def get_query(self):
        if not self.is_bound:
            return
        
        (filter_arg_val, query_string) = self.get_filter_action_and_query()
        filter_on_str = self.cleaned_data['filter_on']
        filter_on_vals = FILTERABLE_FIELDS_DICT.get(filter_on_str, [])

        query_expression = Q()

        for filter_on_val in filter_on_vals:
            query_expression |= Q(**{'%s%s' % (filter_on_val, filter_arg_val): query_string})

        return query_expression


    def clean(self):
        cleaned_data = super().clean()
        if 'filter' in cleaned_data and cleaned_data['filter'] == 'regex':
            qs = cleaned_data['query_string']
            try:
                re.compile(qs)
            except Exception:
                self.add_error('query_string', forms.ValidationError(_('Expresión regular no válida.')))


# TODO: create an abstract superclass that this is an extension of.
class BaseLexiconQueryComposerFormset(forms.BaseFormSet):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS

    CONTROLLED_VOCAB_FIELDS = {
        'part_of_speech': settings.LANGUAGE_CONFIGURATION['azz']['part_of_speech'],
        'inflectional_type': settings.LANGUAGE_CONFIGURATION['azz']['inflectional_type'],
    }

    @property
    def configuration_data(self):
        config = {
            'filterable_fields': self.FILTERABLE_FIELDS,
            'controlled_vocab_fields': self.CONTROLLED_VOCAB_FIELDS,
        }
        return config
    
    @property
    def configuration_data_as_json(self):
        return json.dumps(
            self.configuration_data,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        )
    
    def get_full_query(self):
        query = None

        for form in self.forms:
            if form.is_valid():
                form_q = form.get_query()
                operator = form.cleaned_data['operator']
                if not query:
                    if operator == 'and_n' or operator == 'or_n':
                        query = ~form_q
                    else:
                        query = form_q
                else:
                    if operator == 'and':
                        query &= form_q
                    elif operator == 'or':
                        query |= form_q
                    elif operator == 'and_n':
                        query &= (~form_q)
                    elif operator == 'or_n':
                        query |= (~form_q)
        
        return query



LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)

