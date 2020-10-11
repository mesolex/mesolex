from wagtail.core import blocks
from wagtail.documents import blocks as document_blocks


# Site homepage language family menu structural blocks

class LanguageLinkBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=False)
    language_page = blocks.PageChooserBlock(page_type='mesolex_site.LanguageHomePage')

    class Meta:
        icon = 'user'
        template = 'mesolex_site/blocks/language_family/link.html'


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
