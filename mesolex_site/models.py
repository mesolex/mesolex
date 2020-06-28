from django.db import models
# from django.utils.translation import gettext as _

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtailtrans.models import TranslatablePage


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