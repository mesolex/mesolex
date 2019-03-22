import functools
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise


def contains_word_to_regex(filter_name, filter_action, query_string, _form_data):
    if filter_name != 'contains_word':
        return (filter_action, query_string)

    new_query_string = '(?:^|\s|\.){query_string}(?:$|\s|\.)'.format(
        query_string=query_string,
    )
    return ('__iregex', new_query_string)


def transformation(data_field=None):
    """
    Turns a simple string-to-string function into a transformation
    ready to be plugged into a QueryBuilderForm's transformation
    pipeline.
    """
    def decorator(transformer_fn):
        @functools.wraps(transformer_fn)
        def wrapper(
            filter_name,
            filter_action,
            query_string,
            form_data,
        ):
            if not form_data.get(data_field, None):
                return (filter_action, query_string)
            
            transformed_qstring = transformer_fn(query_string)
            
            if filter_name in ['begins_with', 'exactly_equals']:
                transformed_qstring = '^' + transformed_qstring

            if filter_name in ['ends_with', 'exactly_equals']:
                transformed_qstring = transformed_qstring + '$'

            return ('__iregex', transformed_qstring)

        # Stash a reference to the original for the sake of testing,
        # where we seldom care about the transformation-pipe aspect
        # of all this
        wrapper._original_fn = transformer_fn
        return wrapper
    return decorator


@transformation(data_field='vln')
def to_vln(query_string):
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
    return re.sub(r'([aeiouAEIOU]):?', r'\1:?', query_string)


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