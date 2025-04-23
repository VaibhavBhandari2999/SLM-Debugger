import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or included in the documentation.
    
    This function is used to filter out members of a class based on specific criteria. It checks if the member name is 'skipmeth' and returns True to skip it. If the member name is '_privatemeth', it returns False to include it.
    
    Parameters:
    app (object): The application object, typically the Sphinx application.
    what (str): The type of the object ('module', 'class
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
