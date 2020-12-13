from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from wagtail.core import blocks
from wagtail.documents import blocks as document_blocks


# Site homepage language family menu structural blocks

class LanguageLinkBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=False)
    language_page = blocks.PageChooserBlock(
        page_type='mesolex_site.LanguageHomePage',
        required=False,
    )
    external_url = blocks.URLBlock(required=False)

    class Meta:
        icon = 'user'
        template = 'mesolex_site/blocks/language_family/link.html'

    def clean(self, value):
        name = value.get('name')
        page = value.get('language_page')
        url = value.get('external_url')

        if page is None and url == '':
            raise ValidationError(
                'Validation error in Language Link Block',
                params={
                    'language_page': ErrorList([
                        ValidationError('You must either choose a language page or enter a URL.'),
                    ]),
                },
            )

        if page is not None and url != '':
            raise ValidationError(
                'Validation error in Language Link Block',
                params={
                    'external_url': ErrorList([
                        ValidationError('You cannot both choose a page and enter a URL.'),
                    ]),
                },
            )

        if url != '' and name == '':
            raise ValidationError(
                'Validation error in Language Link Block',
                params={
                    'name': ErrorList([
                        ValidationError(
                            'If you choose an external URL, you must enter a link name.',
                        ),
                    ]),
                },
            )

        return super().clean(value)


class LanguageFamilyBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    languages = blocks.ListBlock(LanguageLinkBlock())

    class Meta:
        icon = 'group'
        template = 'mesolex_site/blocks/language_family/family.html'


class LanguageFamilyMenuBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    language_families = blocks.ListBlock(LanguageFamilyBlock())

    class Meta:
        icon = 'site'
        template = 'mesolex_site/blocks/language_family/menu.html'


# Language page resource menu structural blocks

# NOTE: this block accepts _completely empty_ values for all fields,
# meaning it can be used for placeholder links that go nowhere.
class ResourceLinkBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=False)
    resource_page = blocks.PageChooserBlock(
        page_type=[
            'mesolex_site.LanguageResourcePage',
            'mesolex_site.SearchPage',
        ],
        required=False,
    )
    document = document_blocks.DocumentChooserBlock(required=False)

    class Meta:
        icon = 'doc-full'
        template = 'mesolex_site/blocks/language_resources/resource_link_block.html'
