# Basic unittests to test functioning of module's top-level

from sklearn.utils.testing import assert_equal

__author__ = 'Yaroslav Halchenko'
__license__ = 'BSD'


try:
    from sklearn import *  # noqa
    _top_import_error = None
except Exception as e:
    _top_import_error = e


def test_import_skl():
    """
    Test the import of scikit-learn.
    
    This function checks whether the scikit-learn library can be imported
    successfully. It sets up a variable `_top_import_error` to capture any
    errors that occur during the import process. If the import is successful,
    the function asserts that `_top_import_error` is `None`.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Test either above import has failed for some reason
    # "import *" is discouraged outside of the module level, hence we
    # rely on setting up the variable above
    assert_equal(_top_import_error, None)
