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
from query_builder.utils import SearchContextBuilder


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

    def get_context(self, request):
        context = super().get_context(request)
        search_context = SearchContextBuilder.get_context(request)

        return {
            **context,
            **search_context,
        }


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
