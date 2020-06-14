import json

from django.conf import settings
from django.shortcuts import render

from lexicon.forms import formset_for_lg
from narratives.forms import SoundMetadataQueryComposerFormset
from mesolex.config import DEFAULT_LANGUAGE, LANGUAGES
from mesolex.utils import (
    ForceProxyEncoder,
)

def get_default_data_for_narratives():
    language = LANGUAGES['narratives']
    
    return [{
        'filter': 'begins_with',
        'filter_on': language['filterable_fields'][0]['field'],
        'operator': 'and',
        'query_string': '',
    }]


def get_default_data_for_lg(language):
    if language is None:
        language = LANGUAGES[DEFAULT_LANGUAGE]
    
    return [{
        'filter': 'begins_with',
        'filter_on': language['filterable_fields'][0]['field'],
        'operator': 'and',
        'query_string': '',
    }]


def home(request, *args, **kwargs):
    template_name = 'home.html'
    return render(request, template_name, {
        'languages': json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
        'lexicon': {
            'formset': formset_for_lg(None),
            'formset_data': json.dumps(get_default_data_for_lg(None)),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
        'narratives': {
            'formset': SoundMetadataQueryComposerFormset(),
            'formset_data': json.dumps(get_default_data_for_narratives()),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
    })

