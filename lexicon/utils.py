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
