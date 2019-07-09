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

from lexicon.documents import LexicalEntryDocument
from lexicon.transformations.nahuat_orthography import nahuat_orthography


# TODO: investigate why these gettext-strings have to be
# lazy to work as expected when serialized by the formset.
FILTERABLE_FIELDS = [
    ('lemma', _('Entrada')),
    ('gloss', _('Glosa')),
    ('root', _('Raiz')),
    ('category', _('Campo semántico')),
    ('part_of_speech', _('Categoría gramatical')),
    ('inflectional_type', _('Inflexión')),
]

FILTERABLE_FIELDS_DICT = {
    'lemma': ('lemma', 'variant__value'),
    'gloss': ('gloss__value', ),
    'root': ('root__value', ),
    'category': ('category__value', ),
    'part_of_speech': ('grammargroup__part_of_speech', ),
    'inflectional_type': ('grammargroup__inflectional_type', ),
}

ELASTICSEARCH_FIELDS = [
    ('meaning', _('Defined meaning')),
    ('described_meaning', _('Described meaning')),
    ('contextual_meaning', _('Contextual meaning')),
    ('all_meaning', _('Meaning (all)')),
    ('quotations', _('Citas')),
]

ELASTICSEARCH_FIELDS_DICT = {
    'meaning': ['definitions_es'],
    'described_meaning': ['definitions_es', 'nsem_es'],
    'contextual_meaning': ['definitions_es', 'quotations_es'],
    'all_meaning': ['definitions_es', 'nsem_es', 'quotations_es'],
    'quotations': ['quotations_es', 'quotations_azz'],
}


class LexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS
    FILTERABLE_FIELDS_DICT = FILTERABLE_FIELDS_DICT
    ELASTICSEARCH_FIELDS = ELASTICSEARCH_FIELDS
    ELASTICSEARCH_FIELDS_DICT = ELASTICSEARCH_FIELDS_DICT

    DocumentClass = LexicalEntryDocument

    vln = forms.BooleanField(required=False)
    nahuat_orthography = forms.BooleanField(required=False)

    @property
    def transformations(self):
        return super().transformations + [
            nahuat_orthography,
            to_vln,
        ]


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        if only_with_sound:
            return Q(media__isnull=(not only_with_sound))
        return Q()


class BaseLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = FILTERABLE_FIELDS + ELASTICSEARCH_FIELDS
    TEXT_SEARCH_FIELDS = [field[0] for field in ELASTICSEARCH_FIELDS]

    CONTROLLED_VOCAB_FIELDS = {
        'part_of_speech': settings.LANGUAGE_CONFIGURATION['azz']['part_of_speech'],
        'inflectional_type': settings.LANGUAGE_CONFIGURATION['azz']['inflectional_type'],
    }


LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)

