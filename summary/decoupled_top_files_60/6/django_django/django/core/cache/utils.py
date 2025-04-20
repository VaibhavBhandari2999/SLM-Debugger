import hashlib
from urllib.parse import quote

TEMPLATE_FRAGMENT_KEY_TEMPLATE = 'template.cache.%s.%s'


def make_template_fragment_key(fragment_name, vary_on=None):
    """
    Generates a unique cache key for a template fragment based on the fragment name and varying parameters.
    
    This function is used to create a cache key for a template fragment, which is useful for caching rendered template parts. The key is generated based on the fragment name and any varying parameters that should affect the cache key.
    
    Parameters:
    fragment_name (str): The name of the template fragment.
    vary_on (tuple, optional): A tuple of parameters that should vary the cache key. Defaults to an empty
    """

    if vary_on is None:
        vary_on = ()
    key = ':'.join(quote(str(var)) for var in vary_on)
    args = hashlib.md5(key.encode())
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, args.hexdigest())
