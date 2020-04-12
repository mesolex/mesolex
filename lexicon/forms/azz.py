from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderGlobalFiltersForm,
    QueryBuilderDatasetsForm,
    QueryBuilderBaseFormset,
)

from mesolex.config import LANGUAGES
from mesolex.utils import (
    Language,
    to_vln,
)

from lexicon.documents import LexicalEntryDocument
from lexicon.transformations.nahuat_orthography import nahuat_orthography


Azz = Language('azz')


class LexicalSearchFilterForm(QueryBuilderForm):
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


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        if only_with_sound:
            return Q(media__isnull=(not only_with_sound))
        return Q()


class LexiconQueryBuilderDatasetsForm(QueryBuilderDatasetsForm):
    dataset = forms.ChoiceField(
        choices=[(l['code'], l['label']) for l in LANGUAGES.values()],
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

class BaseLexiconQueryComposerFormset(QueryBuilderBaseFormset):
    global_filters_class = LexiconQueryBuilderGlobalFiltersForm

    FILTERABLE_FIELDS = Azz.filterable_fields + Azz.elasticsearch_fields
    TEXT_SEARCH_FIELDS = [field[0] for field in Azz.elasticsearch_fields_dict]

    CONTROLLED_VOCAB_FIELDS = {
        field['field']: [(item['value'], item['label']) for item in field['items']]
        for field in LANGUAGES['azz']['controlled_vocab_fields']
    }


LexicalSearchFilterFormset = forms.formset_factory(
    LexicalSearchFilterForm,
    formset=BaseLexiconQueryComposerFormset,
)
