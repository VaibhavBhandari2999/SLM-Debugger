import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or included in the documentation.
    
    This function is used to filter out specific members of a class when generating documentation. It checks if the member is named 'skipmeth' and skips it, or if the member is named '_privatemeth' and includes it.
    
    Parameters:
    app (object): The application object, typically part of the Sphinx documentation toolchain.
    what (str): The type of the object being documented ('module', '
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
