import re

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise


def to_vln(filter, query_string):
    """
    Convert a filter + query string combination into a regular expression
    query that applies vowel length neutralization.

    This works by consuming sequences consisting of a vowel plus an
    optional length mark and replacing them with a regex term
    consisting of that vowel plus an optional-flagged length mark.
    The resulting expression is composed with string-boundary symbols
    as appropriate for the filter type. For example, a "begins with"
    query will have the string start character prepended to it.
    """
    if filter == 'regex':
        return ('__iregex', query_string)
    with_neutralization = re.sub(r'([aeiouAEIOU]):?', r'\1:?', query_string)

    affixed_qstr = with_neutralization
    if filter == 'begins_with' or filter == 'exactly_equals':
        affixed_qstr = '^' + affixed_qstr

    if filter == 'ends_with' or filter == 'exactly_equals':
        affixed_qstr = affixed_qstr + '$'

    return ('__iregex', affixed_qstr)


class ForceProxyEncoder(DjangoJSONEncoder):
    """
    Special JSON encoder to allow us to serialize nested values
    containing strings wrapped by ugettext_lazy. This is necessary
    when, for example, passing over language configuration from
    settings, since human-readable equivalents of grammatical
    and inflectional categories will be wrapped by _().
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super().default(obj)
