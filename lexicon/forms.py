import json
import re

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderBaseFormset,
)

from mesolex.utils import (
    to_vln,
)


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


class LexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS
    FILTERABLE_FIELDS_DICT = FILTERABLE_FIELDS_DICT

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
            filter_arg_val = self.FILTERS_DICT.get(filter_str, '')
            query_string = form_data['query_string']
        
        return (filter_arg_val, query_string)


class BaseLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS

    CONTROLLED_VOCAB_FIELDS = {
        'part_of_speech': settings.LANGUAGE_CONFIGURATION['azz']['part_of_speech'],
        'inflectional_type': settings.LANGUAGE_CONFIGURATION['azz']['inflectional_type'],
    }


LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)

