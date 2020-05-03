from django import forms

from query_builder.forms import QueryBuilderForm, QueryBuilderBaseFormset

from mesolex.config import LANGUAGES
from mesolex.utils import Language, to_vln

from lexicon.documents import LexicalEntryDocument
from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from lexicon.transformations.nahuat_orthography import nahuat_orthography


Azz = Language('azz')


class AzzLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = Azz.filterable_fields
    FILTERABLE_FIELDS_DICT = Azz.filterable_fields_dict
    ELASTICSEARCH_FIELDS = Azz.elasticsearch_fields
    ELASTICSEARCH_FIELDS_DICT = Azz.elasticsearch_fields_dict

    DocumentClass = LexicalEntryDocument

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

    FILTERABLE_FIELDS = Azz.filterable_fields + Azz.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in Azz.elasticsearch_fields_dict]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['azz']['controlled_vocab_fields']
    }


AzzLexicalSearchFilterFormset = forms.formset_factory(
    AzzLexicalSearchFilterForm,
    formset=BaseAzzLexiconQueryComposerFormset,
)
