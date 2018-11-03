import logging

from django import template

logger = logging.getLogger()
register = template.Library()


@register.simple_tag(takes_context=True)
def build_absolute_uri(context, url):
    """Add domain information if the specified URL is internal."""
    try:
        return context['request'].build_absolute_uri(url)
    except:
        logger.exception("build_absolute_uri error for url %s", url)
        return ''
