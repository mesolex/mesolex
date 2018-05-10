from django import template

register = template.Library()


@register.filter()
def ensure_list(obj):
    return None if not obj else (obj if isinstance(obj, list) else [obj])
