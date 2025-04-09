from django.utils.itercompat import is_iterable


def make_hashable(value):
    """
    Converts a given value to a hashable format.
    
    This function takes an input value and converts it into a hashable format,
    which can be used as a dictionary key or stored in a set. It handles nested
    dictionaries by converting them into tuples of key-value pairs, where each
    value is recursively processed using the same function. For iterables that
    are not hashable, such as lists or sets, the function converts them into
    tuples of their elements.
    """

    if isinstance(value, dict):
        return tuple([
            (key, make_hashable(nested_value))
            for key, nested_value in value.items()
        ])
    # Try hash to avoid converting a hashable iterable (e.g. string, frozenset)
    # to a tuple.
    try:
        hash(value)
    except TypeError:
        if is_iterable(value):
            return tuple(map(make_hashable, value))
        # Non-hashable, non-iterable.
        raise
    return value
