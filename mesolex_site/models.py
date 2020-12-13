import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtailtrans.models import TranslatablePage

from lexicon.forms import formset_for_lg
from lexicon.models import Entry
from mesolex.config import DEFAULT_LANGUAGE, LANGUAGES
from mesolex.utils import ForceProxyEncoder, get_default_data_for_lg
from mesolex_site.blocks import LanguageFamilyMenuBlock, ResourceLinkBlock


class AbstractHomePage(TranslatablePage):
    """
    A base class for 'homepage-like' pages, which include the site
    homepage and the landing page for each individual language.
    """
    class Meta:
        abstract = True

    headline = models.CharField(max_length=255)
    sub_headline = models.CharField(max_length=255)
    header_img = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = RichTextField(blank=True, null=True)

    # panels
    content_panels = TranslatablePage.content_panels + [
        MultiFieldPanel([
            # TODO: translate
            FieldPanel('headline'),
            FieldPanel('sub_headline', 'Sub-Headline'),
            ImageChooserPanel('header_img', 'Header image'),
        ]),

        FieldPanel('body', classname='full'),
    ]


class HomePage(AbstractHomePage):
    """
    The overall homepage for the site, which exists mainly
    to link out to individual language resource sections and
    host the main menu.
    """
    language_family_menu = StreamField(
        [('language_families', LanguageFamilyMenuBlock())],
        blank=True,
    )
    content_panels = AbstractHomePage.content_panels + [
        InlinePanel('language_links', label='Carousel language links'),
        StreamFieldPanel('language_family_menu'),
    ]


class LanguageHomePage(AbstractHomePage):
    """
    The landing page for each individual language site, which
    links to the language's resources.
    """
    language_code = models.CharField(max_length=255)

    settings_panels = TranslatablePage.settings_panels + [
        FieldPanel('language_code'),
    ]

    # Dedicated links to the core language resource types.
    lexical_resources = StreamField(
        [('lexical_resource_link', ResourceLinkBlock())],
        blank=True,
    )
    corpus_resources = StreamField(
        [('corpus_resource_link', ResourceLinkBlock())],
        blank=True,
    )
    grammatical_resources = StreamField(
        [('grammatical_resource_link', ResourceLinkBlock())],
        blank=True,
    )

    about = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = TranslatablePage.content_panels + [
        MultiFieldPanel([
            # TODO: translate
            FieldPanel('headline'),
            FieldPanel('sub_headline', 'Sub-Headline'),
            ImageChooserPanel('header_img', 'Header image'),
        ]),

        MultiFieldPanel([
            StreamFieldPanel('lexical_resources'),
            StreamFieldPanel('corpus_resources'),
            StreamFieldPanel('grammatical_resources'),
            PageChooserPanel('about', 'mesolex_site.LanguageResourcePage'),
        ]),

        FieldPanel('body', classname='full'),
    ]

    subpage_types = [
        'LanguageResourcePage',
        'SearchPage',
    ]

    parent_page_types = [
        HomePage,
    ]


class LanguageResourcePage(TranslatablePage):
    """
    A basic page with a freeform body field for adding
    language resources.
    """
    body = RichTextField(blank=True, null=True)

    parent_page_types = [
        LanguageHomePage,
        'LanguageResourcePage',
    ]

    content_panels = TranslatablePage.content_panels + [
        FieldPanel('body', classname='full'),
    ]


class SearchPage(TranslatablePage):
    body = RichTextField(blank=True, null=True)

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
            display_entries=None,
            paginator=None,
            result_page=1,
    ):
        return {
            'lexical_entries': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': paginator.count if paginator else 0,
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

        lexical_entries = Entry.objects.filter(query).distinct().order_by('value')

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
                display_entries=display_entries,
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


class HomePageLanguageLink(Orderable):
    home_page = ParentalKey(
        'mesolex_site.HomePage',
        blank=False,
        on_delete=models.CASCADE,
        related_name='language_links',
    )
    language_page = models.ForeignKey(
        'mesolex_site.LanguageHomePage',
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
    )

    short_name = models.CharField(max_length=128, blank=True)
    headline = models.CharField(max_length=255, blank=True)
    sub_headline = models.CharField(max_length=255, blank=True)
    header_img = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        PageChooserPanel('language_page', 'mesolex_site.LanguageHomePage'),
        MultiFieldPanel([
            # TODO: translate
            FieldPanel('short_name'),
            FieldPanel('headline'),
            FieldPanel('sub_headline', 'Sub-Headline'),
            ImageChooserPanel('header_img', 'Header image'),
        ]),
    ]
