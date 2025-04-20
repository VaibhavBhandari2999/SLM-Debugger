from django.utils.itercompat import is_iterable


def make_hashable(value):
    """
    Converts a value to a hashable type. If the value is a dictionary, it converts it into a tuple of key-value pairs, where each value is recursively processed by the same function. If the value is an iterable (excluding dictionaries), it converts the iterable into a tuple of recursively processed elements. If the value is non-iterable and non-dict, it attempts to hash it. If hashing fails, it raises a TypeError.
    
    Parameters:
    value: The input value to be converted
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
