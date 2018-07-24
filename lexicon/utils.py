import re

def get_list_safe(kv, key):
    """
    Helper function to preprocess unreliably typed data from the JSON
    documents representing lexical entries.

    Takes a dict-like object `kv` and returns a list of values
    based on the value of `kv[key]`.

    When some attribute of lexical entry data *can* be a list (or other
    collection), it becomes necessary to treat it as *always* being such
    a collection. An easy way to do this is to normalize the data at
    the point of use by converting empty values to empty lists and
    singular values to one-item lists.
    """
    val = kv[key] if key in kv and kv[key] else []
    return val if isinstance(val, list) else [val]


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
