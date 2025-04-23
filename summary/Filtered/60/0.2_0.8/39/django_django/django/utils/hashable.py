from django.utils.itercompat import is_iterable


def make_hashable(value):
    """
    Converts a value to a hashable form.
    
    This function takes a value and converts it to a hashable form. If the value is a dictionary, it converts the dictionary into a tuple of key-value pairs, where each value is recursively processed by this function. For non-dictionary iterables, it converts them into a tuple of their elements, with each element being recursively processed. Non-iterable and non-dictionary values are hashed if possible; otherwise, a TypeError is raised.
    
    Parameters:
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
