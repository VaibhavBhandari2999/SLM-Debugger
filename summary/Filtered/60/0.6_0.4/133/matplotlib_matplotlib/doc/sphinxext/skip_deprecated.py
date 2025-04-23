# Skip deprecated members


def skip_deprecated(app, what, name, obj, skip, options):
    """
    Function to skip deprecated members in the documentation.
    
    This function is designed to filter out deprecated members from being included in the documentation. It checks if a module is in a predefined list of modules that contain deprecated members and if the current object's name is in the list of deprecated names for that module.
    
    Parameters:
    app (object): The Sphinx application object.
    what (str): The type of the object ('module', 'class', 'exception', 'function', 'method', 'attribute').
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
