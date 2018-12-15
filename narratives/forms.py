from django import forms

from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderBaseFormset,
)


FILTERABLE_FIELDS = (
    ('subgenre', 'subgenre'),
    ('consultant_name', 'consultant name'),
    ('village_of_recording', 'village of recording'),
    ('title', 'title'),
)
FILTERABLE_FIELDS_DICT = {
    'subgenre': ('subgenre', ),
    'consultant_name': ('contr1', 'contr2', ),
    'village_of_recording': ('con1_origin', 'con2_origin', ),
    'title': ('titspn', 'titeng', ),
}


class SoundMetadataSearchFilterForm(QueryBuilderForm):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS
    FILTERABLE_FIELDS_DICT = FILTERABLE_FIELDS_DICT


class BaseSoundMetadataQueryComposerFormset(QueryBuilderBaseFormset):
    FILTERABLE_FIELDS = FILTERABLE_FIELDS

SoundMetadataQueryComposerFormset = forms.formset_factory(
    SoundMetadataSearchFilterForm,
    formset=BaseSoundMetadataQueryComposerFormset,
)