import json

from django.conf import settings
from django.shortcuts import render

from lexicon.forms import LexicalSearchFilterFormset
from narratives.forms import SoundMetadataQueryComposerFormset
from mesolex.config import LANGUAGES
from mesolex.utils import (
    ForceProxyEncoder,
)


def home(request, *args, **kwargs):
    template_name = 'home.html'
    return render(request, template_name, {
        'languages': json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
        'lexicon': {
            'formset': LexicalSearchFilterFormset(),
            'formset_data': json.dumps([]),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
        'narratives': {
            'formset': SoundMetadataQueryComposerFormset(),
            'formset_data': json.dumps([]),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
    })

