from wagtail.core import blocks


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
