from django import forms

from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from mesolex.config import DATASETS
from mesolex.utils import Dataset
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm

PNO = Dataset('plantnames_oax')


class PnoLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = PNO.filterable_fields
    FILTERABLE_FIELDS_DICT = PNO.filterable_fields_dict
    SEARCH_FIELDS = PNO.search_fields
    SEARCH_FIELDS_DICT = PNO.search_fields_dict


class BasePnoLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = PNO.filterable_fields + PNO.search_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in PNO.search_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in DATASETS['trq']['controlled_vocab_fields']
    }


PnoLexicalSearchFilterFormset = forms.formset_factory(
    PnoLexicalSearchFilterForm,
    formset=BasePnoLexiconQueryComposerFormset,
)
