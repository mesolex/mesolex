import functools


def transformation(data_field=None):
    """
    Turns a simple string-to-string function into a transformation
    ready to be plugged into a transformation pipeline.
    """
    def decorator(transformer_fn):
        @functools.wraps(transformer_fn)
        def wrapper(
                filter_type,
                value,
                modifiers,
        ):
            if not data_field in modifiers:
                return (filter_type, value)

            new_value = transformer_fn(value)

            if filter_type in ['begins_with', 'exactly_equals']:
                new_value = '^' + new_value

            if filter_type in ['ends_with', 'exactly_equals']:
                new_value = new_value + '$'

            return ('regex', new_value)

        # Stash a reference to the original for the sake of testing,
        # where we seldom care about the transformation-pipe aspect
        # of all this
        wrapper._original_fn = transformer_fn
        return wrapper
    return decorator


def apply_transformations(
        filter_type,
        value,
        modifiers,
        transformations
):
    for transformation_fn in transformations:
        (filter_type, value) = transformation_fn(filter_type, value, modifiers)

    return (filter_type, value)
