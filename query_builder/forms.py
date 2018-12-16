import json
import re

from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from mesolex.utils import (
    to_vln,
    ForceProxyEncoder,
)


class QueryBuilderForm(forms.Form):
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

    # NOTE: abstract, must be filled in with sequence of pairs,
    # e.g. ``('lemma', _('Entrada'))``
    FILTERABLE_FIELDS = []

    # NOTE: abstract, must be filled in with dictionary
    # enumerating the fields to touch with a given query
    # field, e.g. ``'lemma': ('lemma', 'variant__value')``.
    FILTERABLE_FIELDS_DICT = {}

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filter_on'] = forms.ChoiceField(
            choices=self.FILTERABLE_FIELDS,
            widget=forms.Select(attrs={'class': 'custom-select'})
        )

    def get_filter_action_and_query(self):
        """
        NOTE: this will have to be overridden if anything interesting
        is done to generate a query string and filter action, e.g.
        if there is a "vowel length neutralization" feature or some such.
        """
        
        if not self.is_bound:
            return (None, None)
        
        form_data = self.cleaned_data
        filter_str = form_data['filter']
        filter_arg_val = self.FILTERS_DICT.get(filter_str, '')
        query_string = form_data['query_string']
        
        return (filter_arg_val, query_string)

    def get_query(self):
        if not self.is_bound:
            return
        
        (filter_arg_val, query_string) = self.get_filter_action_and_query()
        filter_on_str = self.cleaned_data['filter_on']
        filter_on_vals = self.FILTERABLE_FIELDS_DICT.get(filter_on_str, [])

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


class QueryBuilderBaseFormset(forms.BaseFormSet):
    # NOTE: abstract, must be filled in with sequence of pairs,
    # e.g. ``('lemma', _('Entrada'))``
    FILTERABLE_FIELDS = []

    # NOTE: abstract, must be filled in with dictionary of
    # controlled vocabulary fields and their pair values.
    CONTROLLED_VOCAB_FIELDS = {}

    # Available for overriding if fields must
    # be computed dynamically.
    @property
    def filterable_fields(self):
        return self.FILTERABLE_FIELDS

    @property
    def controlled_vocab_fields(self):
        return self.CONTROLLED_VOCAB_FIELDS

    @property
    def configuration_data(self):
        config = {
            'filterable_fields': self.filterable_fields,
            'controlled_vocab_fields': self.controlled_vocab_fields,
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