from django import forms

from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from mesolex.config import DATASETS
from mesolex.utils import Dataset
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm

TRQ = Dataset('trq')


class TrqLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = TRQ.filterable_fields
    FILTERABLE_FIELDS_DICT = TRQ.filterable_fields_dict
    SEARCH_FIELDS = TRQ.search_fields
    SEARCH_FIELDS_DICT = TRQ.search_fields_dict


class BaseTrqLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = TRQ.filterable_fields + TRQ.search_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in TRQ.search_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in DATASETS['trq']['controlled_vocab_fields']
    }


TrqLexicalSearchFilterFormset = forms.formset_factory(
    TrqLexicalSearchFilterForm,
    formset=BaseTrqLexiconQueryComposerFormset,
)
