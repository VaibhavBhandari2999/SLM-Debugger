import os
import sys

sys.path.insert(0, os.path.abspath('.'))


extensions = ['sphinx.ext.autosummary']
autosummary_generate = True
autodoc_default_options = {'members': True}


def skip_member(app, what, name, obj, skip, options):
    """
    Function to determine whether a member of a class should be skipped or not during documentation generation.
    
    This function is used to customize the behavior of skipping certain members of a class when generating documentation. It checks if the member name matches specific criteria and returns a boolean value indicating whether the member should be skipped.
    
    Parameters:
    app (object): The application object, typically used to access application-specific information.
    what (str): The type of the object being documented. Possible values are 'module', 'class',
    """

    if name == 'skipmeth':
        return True
    elif name == '_privatemeth':
        return False


def setup(app):
    app.connect('autodoc-skip-member', skip_member)
