import re

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.filter()
def ensure_list(obj):
    return None if not obj else (obj if isinstance(obj, list) else [obj])


def _get_querystring(form, filter_on='lemma'):
    """
    Generates the query string for a one-form LexicalSearchFilterFormset
    searching for ``form`` in the field ``filter_on``.
    """
    return (
        "?form-TOTAL_FORMS=1"
        "&form-INITIAL_FORMS=0"
        "&form-MIN_NUM_FORMS=0"
        "&form-MAX_NUM_FORMS=1000"
        "&form-0-query_string=%s"
        "&form-0-operator=and"
        "&form-0-filter_on=%s"
        "&form-0-filter=exactly_equals"
    ) % (form, filter_on)


@register.filter()
def link_vnawa(text):
    return re.sub(
        r'<vnawa>(.+?)</vnawa>',
        r'<a href="%s%s" class="vnawa">\1</a>' % (
            reverse('lexicon_search'),
            _get_querystring(r'\1'),
        ),
        text,
    )


@register.filter()
def link_raiz(raiz):
    return '<a href="%s%s" class="raiz">%s</a>' % (
        reverse('lexicon_search'),
        _get_querystring(raiz, filter_on='root'),
        raiz,
    )


@register.filter()
def link_category(category):
    return '<a href="%s%s" class="category">%s</a>' % (
        reverse('lexicon_search'),
        _get_querystring(category, filter_on='category'),
        category,
    )
