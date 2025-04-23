# Skip deprecated members


def skip_deprecated(app, what, name, obj, skip, options):
    """
    Function to skip deprecated members in the documentation.
    
    This function is designed to filter out deprecated members from being included in the documentation. It checks if a module is in a predefined list of modules that contain deprecated members and skips those members if they are found.
    
    Parameters:
    app (object): The Sphinx application object.
    what (str): The type of the object being documented ('module', 'class', 'exception', 'function', 'method', 'attribute').
    name (str): The fully qualified
    """

    if skip:
        return skip
    skipped = {"matplotlib.colors": ["ColorConverter", "hex2color", "rgb2hex"]}
    skip_list = skipped.get(getattr(obj, "__module__", None))
    if skip_list is not None:
        return getattr(obj, "__name__", None) in skip_list


def setup(app):
    """
    Setup function for the Sphinx documentation.
    
    This function is designed to be used with the Sphinx documentation system. It connects a custom skip function to the 'autodoc-skip-member' event, ensuring that deprecated members are skipped during the documentation generation process. Additionally, it returns metadata indicating that the function is safe for parallel processing.
    
    Parameters:
    app (Sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: Metadata dictionary with 'parallel_read_safe' and 'parallel_write_safe'
    """

    app.connect('autodoc-skip-member', skip_deprecated)

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}
    return metadata
