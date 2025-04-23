# Skip deprecated members


def skip_deprecated(app, what, name, obj, skip, options):
    if skip:
        return skip
    skipped = {"matplotlib.colors": ["ColorConverter", "hex2color", "rgb2hex"]}
    skip_list = skipped.get(getattr(obj, "__module__", None))
    if skip_list is not None:
        return getattr(obj, "__name__", None) in skip_list


def setup(app):
    """
    Setup function for the Sphinx documentation.
    
    This function connects to the 'autodoc-skip-member' event to skip deprecated members during the documentation generation process. It also returns metadata indicating that the function is safe for parallel reading and writing.
    
    Parameters:
    app (sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: Metadata dictionary containing 'parallel_read_safe' and 'parallel_write_safe' keys set to True.
    """

    app.connect('autodoc-skip-member', skip_deprecated)

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}
    return metadata
