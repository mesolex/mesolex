from django import forms

from lexicon.documents import EntryDocument
from lexicon.transformations.juxt1235 import neutralize_glottal_stop
from mesolex.config import LANGUAGES
from mesolex.utils import Language
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm


JUXT1235 = Language('juxt1235')


class Juxt1235LexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = JUXT1235.filterable_fields
    FILTERABLE_FIELDS_DICT = JUXT1235.filterable_fields_dict

    DocumentClass = EntryDocument

    neutralize_glottal_stop = forms.BooleanField(required=False)

    @property
    def transformations(self):
        return super().transformations + [
            neutralize_glottal_stop,
        ]


class BaseJuxt1235LexiconQueryComposerFormset(QueryBuilderBaseFormset):
    FILTERABLE_FIELDS = JUXT1235.filterable_fields

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['juxt1235']['controlled_vocab_fields']
    }


Juxt1235LexicalSearchFilterFormset = forms.formset_factory(
    Juxt1235LexicalSearchFilterForm,
    formset=BaseJuxt1235LexiconQueryComposerFormset,
)
