from django import forms
from django.utils.translation import ugettext_lazy as _


from query_builder.forms import (
    QueryBuilderForm,
    QueryBuilderBaseFormset,
)

from narratives import models


FILTERABLE_FIELDS = (
    ('subgenre', _('Subgénero')),
    ('consultant_name', _('Nombre del contribuidor')),
    ('village_of_recording', _('Pueblo de grabacion')),
    ('title', _('Título')),
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

    @property
    def controlled_vocab_fields(self):
        subgenres = set([x['subgenre'] for x in models.SoundMetadata.objects.values('subgenre')])
        con1_names = set([x['contr1'] for x in models.SoundMetadata.objects.values('contr1')])
        con2_names = set([x['contr2'] for x in models.SoundMetadata.objects.values('contr2')])
        consultant_names = con1_names.union(con2_names)

        con1_qs = models.SoundMetadata.objects.filter(con1_role='Consultant')
        con2_qs = models.SoundMetadata.objects.filter(con2_role='Consultant')
        con1_vs = set([x['con1_origin'] for x in con1_qs.values('con1_origin')])
        con2_vs = set([x['con2_origin'] for x in con2_qs.values('con2_origin')])
        villages = con1_vs.union(con2_vs)
        return {
            'consultant_name': [(x, x) for x in sorted(consultant_names) if x],
            'subgenre': [(x, x) for x in sorted(subgenres) if x],
            'village_of_recording': [(x, x) for x in sorted(villages) if x],
        }

SoundMetadataQueryComposerFormset = forms.formset_factory(
    SoundMetadataSearchFilterForm,
    formset=BaseSoundMetadataQueryComposerFormset,
)