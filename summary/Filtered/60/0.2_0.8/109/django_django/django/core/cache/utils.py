from django.utils.crypto import md5

TEMPLATE_FRAGMENT_KEY_TEMPLATE = "template.cache.%s.%s"


def make_template_fragment_key(fragment_name, vary_on=None):
    """
    Generates a unique cache key for a template fragment.
    
    This function creates a cache key based on a given fragment name and optional vary-on parameters. The key is used to cache template fragments for efficient rendering.
    
    Parameters:
    fragment_name (str): The name of the template fragment.
    vary_on (list, optional): A list of parameters that should vary the cache key. Each parameter is converted to a string and appended to the key.
    
    Returns:
    str: A unique cache key for the template
    """

    hasher = md5(usedforsecurity=False)
    if vary_on is not None:
        for arg in vary_on:
            hasher.update(str(arg).encode())
            hasher.update(b":")
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, hasher.hexdigest())
