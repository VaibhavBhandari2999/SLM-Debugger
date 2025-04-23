# Skip deprecated members


def skip_deprecated(app, what, name, obj, skip, options):
    """
    Function to determine if a function or class should be skipped in the documentation.
    
    This function checks if the given object (function or class) should be skipped from being documented. It specifically looks for objects in certain modules that are marked as deprecated and should not be included in the documentation.
    
    Parameters:
    app (object): The Sphinx application object.
    what (str): The type of the object ('function', 'class', etc.).
    name (str): The name of the object.
    obj
    """

    if skip:
        return skip
    skipped = {"matplotlib.colors": ["ColorConverter", "hex2color", "rgb2hex"]}
    skip_list = skipped.get(getattr(obj, "__module__", None))
    if skip_list is not None:
        return getattr(obj, "__name__", None) in skip_list


def setup(app):
    app.connect('autodoc-skip-member', skip_deprecated)

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}
    return metadata
 True, 'parallel_write_safe': True}
    return metadata
