from django import forms

from query_builder.forms import QueryBuilderForm, QueryBuilderBaseFormset

from mesolex.config import LANGUAGES
from mesolex.utils import Language

from lexicon.documents import LexicalEntryDocument
from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm


Trq = Language('trq')


class TrqLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = Trq.filterable_fields
    FILTERABLE_FIELDS_DICT = Trq.filterable_fields_dict
    ELASTICSEARCH_FIELDS = Trq.elasticsearch_fields
    ELASTICSEARCH_FIELDS_DICT = Trq.elasticsearch_fields_dict

    DocumentClass = LexicalEntryDocument


class BaseTrqLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = Trq.filterable_fields + Trq.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in Trq.elasticsearch_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['trq']['controlled_vocab_fields']
    }


TrqLexicalSearchFilterFormset = forms.formset_factory(
    TrqLexicalSearchFilterForm,
    formset=BaseTrqLexiconQueryComposerFormset,
)
