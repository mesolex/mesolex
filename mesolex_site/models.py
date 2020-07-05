import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import Lower
from django.db import models
# from django.utils.translation import gettext as _

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtailtrans.models import TranslatablePage

from lexicon.forms import formset_for_lg
from lexicon.models import LexicalEntry
from mesolex.config import DEFAULT_LANGUAGE, LANGUAGES
from mesolex.utils import (
    get_default_data_for_lg,
    ForceProxyEncoder,
)


class HomePage(TranslatablePage):
    # hero image fields
    headline = models.CharField(max_length=255)
    sub_headline = models.CharField(max_length=255)
    header_img = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = RichTextField()

    # panels
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            # TODO: translate
            FieldPanel('headline'),
            FieldPanel('sub_headline', 'Sub-Headline'),
            ImageChooserPanel('header_img', 'Header image'),
        ]),

        FieldPanel('body', classname='full'),
    ]


class SearchPage(TranslatablePage):
    language_code = models.CharField(
        max_length=255,
        default=DEFAULT_LANGUAGE,
    )

    content_panels = Page.content_panels + [
        FieldPanel(
            'language_code',
            widget=forms.Select(
                choices=[
                    (val['code'], val['label'])
                    for val in LANGUAGES.values()
                ],
            ),
        ),
    ]

    def _search_query_data(
        self,
        formset,
        lexical_entries = None,
        display_entries = None,
        query = None,
        paginator = None,
        result_page = 1,
    ):
        return {
            'lexical_entries': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': lexical_entries.count() if lexical_entries else 0,
            'result_page': result_page,
            'query': True,
            'languages': json.dumps(
                LANGUAGES,
                ensure_ascii=False,
                cls=ForceProxyEncoder,
            ),
            'search': {
                'formset': formset,
                'formset_global_filters_form': formset.global_filters_form,
                'formset_data': json.dumps([form.cleaned_data for form in formset.forms]),
                'formset_global_filters_form_data': json.dumps(formset.global_filters_form.data),
                'formset_datasets_form': formset.datasets_form,
                'formset_datasets_form_data': json.dumps(formset.datasets_form.data),
                'formset_errors': json.dumps(formset.errors),
            },
            'language': formset.data.get('dataset', 'azz')
        }

    def _search_context(self, request, context):
        formset_class = formset_for_lg(request.GET.get('dataset'))
        formset = formset_class(request.GET)        

        try:
            query = formset.get_full_query()
        except ValidationError:
            # The formset has been tampered with.
            # Django doesn't handle this very gracefully.
            # To prevent a 500 error, just bail out here.
            # TODO: make this nicer.
            return {**context, **self._search_query_data(formset_class())}

        lexical_entries = (
            LexicalEntry.valid_entries
            .filter(query)
            .annotate(lower_lemma=Lower('lemma'))
            .order_by('lower_lemma')
        )
        paginator = Paginator(lexical_entries, 25)
        result_page = request.GET.get('page', 1)

        try:
            display_entries = paginator.page(result_page)
        except PageNotAnInteger:
            display_entries = paginator.page(1)
        except EmptyPage:
            display_entries = paginator.page(paginator.num_pages)
            result_page = paginator.num_pages

        return {
            **context,
            **self._search_query_data(
                formset,
                lexical_entries=lexical_entries,
                display_entries=display_entries,
                query=query,
                paginator=paginator,
                result_page=result_page,
            ),
        }

    def get_context(self, request):
        context = super().get_context(request)

        formset = formset_for_lg(None)()

        if request.GET:
            return self._search_context(request, context)

        context['languages'] = json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        )

        context['search'] = {
            'formset': formset,
            'formset_datasets_form_data': json.dumps([]),
            'formset_global_filters_form_data': json.dumps([]),
            'formset_data': json.dumps(get_default_data_for_lg(None)),
            'formset_errors': json.dumps([]),
        }

        return context