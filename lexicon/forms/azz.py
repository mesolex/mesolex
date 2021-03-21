from django import forms

from lexicon.documents import EntryDocument
from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from lexicon.transformations.nahuat_orthography import nahuat_orthography
from mesolex.config import DATASETS
from mesolex.utils import Dataset, to_vln
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm

AZZ = Dataset('azz')


class AzzLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = AZZ.filterable_fields
    FILTERABLE_FIELDS_DICT = AZZ.filterable_fields_dict
    ELASTICSEARCH_FIELDS = AZZ.elasticsearch_fields
    ELASTICSEARCH_FIELDS_DICT = AZZ.elasticsearch_fields_dict

    DocumentClass = EntryDocument

    vln = forms.BooleanField(required=False)
    nahuat_orthography = forms.BooleanField(required=False)

    @property
    def transformations(self):
        return super().transformations + [
            nahuat_orthography,
            to_vln,
        ]


class BaseAzzLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = AZZ.filterable_fields + AZZ.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in AZZ.elasticsearch_fields]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in DATASETS['azz']['controlled_vocab_fields']
    }


AzzLexicalSearchFilterFormset = forms.formset_factory(
    AzzLexicalSearchFilterForm,
    formset=BaseAzzLexiconQueryComposerFormset,
)
