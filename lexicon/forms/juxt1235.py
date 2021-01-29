from django import forms

from lexicon.documents import EntryDocument
from mesolex.utils import Language
from query_builder.forms import QueryBuilderBaseFormset, QueryBuilderForm


JUXT1235 = Language('juxt1235')


class Juxt1235LexicalSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = JUXT1235.filterable_fields
    FILTERABLE_FIELDS_DICT = JUXT1235.filterable_fields_dict

    DocumentClass = EntryDocument



class BaseJuxt1235LexiconQueryComposerFormset(QueryBuilderBaseFormset):
    FILTERABLE_FIELDS = JUXT1235.filterable_fields


Juxt1235LexicalSearchFilterFormset = forms.formset_factory(
    Juxt1235LexicalSearchFilterForm,
    formset=BaseJuxt1235LexiconQueryComposerFormset,
)
