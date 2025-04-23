import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or not during documentation generation.
    
    This function is used to filter out specific methods or attributes from being included in the documentation. It checks if the name of the member is 'skipmeth' and returns True to skip it, or if the name is '_privatemeth' and returns False to include it.
    
    Parameters:
    app (object): The application object, typically the Sphinx application context.
    what (str): The type of the object
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
