import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member should be skipped in the documentation.
    
    This function is used to filter out specific members from being included in the documentation.
    It checks if the member name is 'skipmeth' and returns True to skip it, or if the member name is '_privatemeth' and returns False to include it.
    
    Parameters:
    app (object): The application object, typically the Sphinx application.
    what (str): The type of the object ('module', 'class', 'exception',
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
