from django.utils.itercompat import is_iterable


def make_hashable(value):
    """
    Converts a value to a hashable type.
    
    This function takes a value and converts it to a hashable type. If the value is a dictionary, it converts the dictionary to a tuple of key-value pairs, where each value is recursively processed by this function. If the value is an iterable (excluding dictionaries), it converts the iterable to a tuple of hashable values. If the value is non-hashable and non-iterable, it raises a TypeError.
    
    Parameters:
    value: The value
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
