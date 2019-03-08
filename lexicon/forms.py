import json
import re

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderGlobalFiltersForm,
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

    @property
    def transformations(self):
        return super().transformations + [
            to_vln,
        ]


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        return Q(media__isnull=(not only_with_sound))


class BaseLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = FILTERABLE_FIELDS

    CONTROLLED_VOCAB_FIELDS = {
        'part_of_speech': settings.LANGUAGE_CONFIGURATION['azz']['part_of_speech'],
        'inflectional_type': settings.LANGUAGE_CONFIGURATION['azz']['inflectional_type'],
    }


LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)

