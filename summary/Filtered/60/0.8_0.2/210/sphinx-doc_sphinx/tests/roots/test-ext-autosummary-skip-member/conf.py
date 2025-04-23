import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to decide whether to skip a member during documentation generation.
    
    This function is used to filter members of a class or module before they are documented. It checks if the member name is 'skipmeth' and skips it, or if the name is '_privatemeth' and includes it.
    
    Parameters:
    app (object): The Sphinx application object.
    what (str): The type of the object being documented ('module', 'class', 'exception', etc.).
    name (str): The
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
