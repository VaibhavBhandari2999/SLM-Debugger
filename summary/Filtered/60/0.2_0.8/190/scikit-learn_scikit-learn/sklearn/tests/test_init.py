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
    Test the successful import of scikit-learn.
    
    This function checks whether the scikit-learn library has been imported
    successfully. It sets up the variable `_top_import_error` to None if the
    import was successful, or to the error message if it failed.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Test either above import has failed for some reason
    # "import *" is discouraged outside of the module level, hence we
    # rely on setting up the variable above
    assert_equal(_top_import_error, None)
