import re

from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlquote
from django.utils.safestring import mark_safe

from mesolex.config import LANGUAGES

register = template.Library()


# Translates the key-value pairs found within the LANGUAGES
# controlled vocab fields into a dictionary, allowing easy lookup
# of human-readable forms for display.

LANGUAGE_CATEGORIES_LOOKUPS = {
    language: {
        field['field']: {
            item['value']: item['label']
            for item in field['items']
        } for field in language_data['controlled_vocab_fields']
    }
    for (language, language_data) in LANGUAGES.items()
}


@register.filter()
def ensure_list(obj):
    return None if not obj else (obj if isinstance(obj, list) else [obj])


def _get_querystring(form, filter_on='lemma'):
    """
    Generates the query string for a one-form LexicalSearchFilterFormset
    searching for ``form`` in the field ``filter_on``.

    TODO: generate this by means of an actual instance of the mechanism
    that generates URLs (as of Sept 13 2020, the formsets).
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


def _get_human_readable(language, category, item):
    """
    Traverse LANGUAGE_CATEGORIES_LOOKUPS to find the human-readable
    equivalent of ``item``. If it's not found, default to returning
    ``item`` itself.
    """
    return LANGUAGE_CATEGORIES_LOOKUPS.get(
        language,
        {},
    ).get(
        category,
        {},
    ).get(
        item,
        item,
    )


@register.filter()
def link_vnawa(text, base_url):
    return mark_safe(re.sub(
        r'<vnawa>(.+?)</vnawa>',
        r'<a href="%s%s" class="vnawa">\1</a>' % (
            base_url,
            _get_querystring(urlquote(r'\1')),
        ),
        text,
    ))


@register.filter()
def link_raiz(raiz, base_url):
    qs = _get_querystring(urlquote(raiz), filter_on='root')
    return mark_safe(f'<a href="{base_url}{qs}" class="raiz">{raiz}</a>')


@register.filter()
def link_category(category, base_url):
    qs = _get_querystring(urlquote(category), filter_on='category')
    return mark_safe(f'<a href="{base_url}{qs}" class="category">{category}</a>')


@register.simple_tag
def link_part_of_speech(pos, base_url, language='azz'):
    return mark_safe('<a href="%s%s" class="pos">%s</a>' % (
        base_url,
        _get_querystring(urlquote(pos), filter_on='part_of_speech'),
        _get_human_readable(language, 'part_of_speech', pos),
    ))


@register.simple_tag
def link_inflectional_type(it, base_url, language='azz'):
    return mark_safe('<a href="%s%s" class="it">%s</a>' % (
        base_url,
        _get_querystring(urlquote(it), filter_on='inflectional_type'),
        _get_human_readable(language, 'inflectional_type', it),
    ))
