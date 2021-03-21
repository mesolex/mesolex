from django import forms

from lexicon.documents import EntryDocument
from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from mesolex.config import DATASETS
from mesolex.utils import Dataset
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm

TRQ = Dataset('trq')


class TrqLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = TRQ.filterable_fields
    FILTERABLE_FIELDS_DICT = TRQ.filterable_fields_dict
    ELASTICSEARCH_FIELDS = TRQ.elasticsearch_fields
    ELASTICSEARCH_FIELDS_DICT = TRQ.elasticsearch_fields_dict

    DocumentClass = EntryDocument


class BaseTrqLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = TRQ.filterable_fields + TRQ.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in TRQ.elasticsearch_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in DATASETS['trq']['controlled_vocab_fields']
    }


TrqLexicalSearchFilterFormset = forms.formset_factory(
    TrqLexicalSearchFilterForm,
    formset=BaseTrqLexiconQueryComposerFormset,
)
