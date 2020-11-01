from django import template

from mesolex_site import models


register = template.Library()


@register.simple_tag(takes_context=True)
def get_language_homepage(context):
    """
    Fetches the nearest ancestor language home page, if it exists.
    This allows you to add the language sub-site's title to the
    header, etc.
    """
    # NOTE: we are leaving this untested because the Wagtail
    # CMS will shortly be replaced by a separate CMS-based site.

    if not 'page' in context:
        return None

    return context['page'].get_ancestors(
        inclusive=True,
    ).type(
        models.LanguageHomePage
    ).first()
