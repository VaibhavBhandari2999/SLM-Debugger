from django.utils.crypto import md5

TEMPLATE_FRAGMENT_KEY_TEMPLATE = "template.cache.%s.%s"


def make_template_fragment_key(fragment_name, vary_on=None):
    """
    Generates a unique template fragment key based on the given fragment name and varying parameters.
    
    Args:
    fragment_name (str): The name of the template fragment.
    vary_on (Optional[List]): A list of arguments to vary the fragment key on.
    
    Returns:
    str: The generated template fragment key.
    
    Notes:
    - Utilizes the `md5` hashing algorithm from the `hashlib` library to generate a unique key.
    - If `vary_on` is provided,
    """

    hasher = md5(usedforsecurity=False)
    if vary_on is not None:
        for arg in vary_on:
            hasher.update(str(arg).encode())
            hasher.update(b":")
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, hasher.hexdigest())
