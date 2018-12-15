import json

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from .forms import (
    SoundMetadataQueryComposerFormset,
)
from .models import SoundMetadata
from mesolex.utils import (
    ForceProxyEncoder,
)


def narratives_search_view(request, *args, **kwargs):
    template_name = 'narratives/search.html'
    if request.GET:
        formset = SoundMetadataQueryComposerFormset(request.GET)
        metadatas = None
        display_entries = None
        query = None
        paginator = None
        page = 1

        if len(formset.forms) >= 1:
            query = formset.get_full_query()

        if query:
            metadatas = (
                SoundMetadata.objects
                .filter(query)
            )
            paginator = Paginator(metadatas, 25)

            page = request.GET.get('page', 1)
            try:
                display_entries = paginator.page(page)
            except PageNotAnInteger:
                display_entries = paginator.page(1)
            except EmptyPage:
                display_entries = paginator.page(paginator.num_pages)
                page = paginator.num_pages

        return render(request, template_name, {
            'metadatas': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': metadatas.count() if metadatas else 0,
            'page': page,
            'query': True,
            'formset': formset,
            'formset_data': json.dumps(formset.data),
            'formset_errors': json.dumps(formset.errors),
        })

    formset = SoundMetadataQueryComposerFormset()
    return render(request, template_name, {
        'formset': formset,
        'formset_data': json.dumps(formset.data),
        'formset_errors': json.dumps(formset.errors),
    })