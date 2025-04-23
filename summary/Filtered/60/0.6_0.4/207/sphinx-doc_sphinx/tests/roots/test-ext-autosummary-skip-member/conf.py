import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or not during documentation generation.
    
    This function is used to filter out or include specific members of a class based on their names. It is particularly useful in controlling which methods or attributes are documented.
    
    Parameters:
    app (object): The application object, typically part of the Sphinx documentation toolchain.
    what (str): The type of the object being documented. Can be 'module', 'class', 'exception', 'function', 'method',
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
