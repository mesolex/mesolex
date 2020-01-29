from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderGlobalFiltersForm,
    QueryBuilderBaseFormset,
)

from mesolex.config import LANGUAGES
from mesolex.utils import (
    to_vln,
)

from lexicon.documents import LexicalEntryDocument
from lexicon.transformations.nahuat_orthography import nahuat_orthography


# TODO: investigate why these gettext-strings have to be
# lazy to work as expected when serialized by the formset.
FILTERABLE_FIELDS = [
    (field['field'], field['label'])
    for field in LANGUAGES['azz']['filterable_fields']
]

FILTERABLE_FIELDS_DICT = {
    field['field']: field['terms']
    for field in LANGUAGES['azz']['filterable_fields']
}

ELASTICSEARCH_FIELDS = [
    (field['field'], field['label'])
    for field in LANGUAGES['azz']['elasticsearch_fields']
]

ELASTICSEARCH_FIELDS_DICT = {
    field['field']: field['terms']
    for field in LANGUAGES['azz']['elasticsearch_fields']
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
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['azz']['controlled_vocab_fields']
    }


LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)
