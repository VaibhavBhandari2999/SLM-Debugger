from django.utils.crypto import md5

TEMPLATE_FRAGMENT_KEY_TEMPLATE = "template.cache.%s.%s"


def make_template_fragment_key(fragment_name, vary_on=None):
    """
    Generates a unique key for a template fragment based on the fragment name and optional varying parameters.
    
    Parameters:
    fragment_name (str): The name of the template fragment.
    vary_on (list, optional): A list of parameters to vary the fragment key. Each parameter is converted to a string and appended to the key.
    
    Returns:
    str: A unique key for the template fragment, which can be used to cache the fragment.
    
    This function is used to generate a unique key for a template fragment
    """

    hasher = md5(usedforsecurity=False)
    if vary_on is not None:
        for arg in vary_on:
            hasher.update(str(arg).encode())
            hasher.update(b":")
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, hasher.hexdigest())
