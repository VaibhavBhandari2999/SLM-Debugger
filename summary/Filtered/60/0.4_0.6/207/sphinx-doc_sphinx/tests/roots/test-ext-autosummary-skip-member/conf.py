import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or included in the documentation.
    
    This function is used to filter out specific members of a class based on their names. It can be used in the context of generating documentation for a class, where certain methods or attributes might need to be excluded or included based on their names.
    
    Parameters:
    app (object): The application object, typically used in the context of Sphinx documentation generation.
    what (str): The type of the object being documented.
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
