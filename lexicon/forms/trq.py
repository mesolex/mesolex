from django import forms

from lexicon.documents import LexicalEntryDocument
from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from mesolex.config import LANGUAGES
from mesolex.utils import Language
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm

TRQ = Language('trq')


class TrqLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = TRQ.filterable_fields
    FILTERABLE_FIELDS_DICT = TRQ.filterable_fields_dict
    ELASTICSEARCH_FIELDS = TRQ.elasticsearch_fields
    ELASTICSEARCH_FIELDS_DICT = TRQ.elasticsearch_fields_dict

    DocumentClass = LexicalEntryDocument


class BaseTrqLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = TRQ.filterable_fields + TRQ.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in TRQ.elasticsearch_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['trq']['controlled_vocab_fields']
    }


TrqLexicalSearchFilterFormset = forms.formset_factory(
    TrqLexicalSearchFilterForm,
    formset=BaseTrqLexiconQueryComposerFormset,
)
