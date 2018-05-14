def plural_data(datum, key):
    """
    Helper function to preprocess unreliably typed data from the JSON
    documents representing lexical entries.

    Takes a dict-like object `datum` and returns a list of values
    based on the value of `datum[key]`.

    When some attribute of lexical entry data *can* be a list (or other
    collection), it becomes necessary to treat it as *always* being such
    a collection. An easy way to do this is to normalize the data at
    the point of use by converting empty values to empty lists and
    singular values to one-item lists.
    """
    if key in datum and datum[key]:
        value = datum[key]
        if isinstance(value, list):
            return value
        else:
            return [value]
    else:
        return []
