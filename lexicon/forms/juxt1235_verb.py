from django import forms

from lexicon.forms.base import LexiconQueryBuilderGlobalFiltersForm
from lexicon.transformations.juxt1235 import neutralize_glottal_stop
from mesolex.config import DATASETS
from mesolex.utils import Dataset
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm


JUXT1235_VERB = Dataset('juxt1235_verb')


class Juxt1235VerbLexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = JUXT1235_VERB.filterable_fields
    FILTERABLE_FIELDS_DICT = JUXT1235_VERB.filterable_fields_dict

    neutralize_glottal_stop = forms.BooleanField(required=False)

    @property
    def transformations(self):
        return super().transformations + [
            neutralize_glottal_stop,
        ]


class BaseJuxt1235VerbLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = JUXT1235_VERB.filterable_fields

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in DATASETS['juxt1235_verb']['controlled_vocab_fields']
    }


Juxt1235VerbLexicalSearchFilterFormset = forms.formset_factory(
    Juxt1235VerbLexicalSearchFilterForm,
    formset=BaseJuxt1235VerbLexiconQueryComposerFormset,
)
