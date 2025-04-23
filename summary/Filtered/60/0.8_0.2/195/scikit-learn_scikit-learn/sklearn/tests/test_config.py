from sklearn import get_config, set_config, config_context
from sklearn.utils.testing import assert_raises


def test_config_context():
    """
    Test the context manager functionality of config_context.
    
    This function tests the behavior of the config_context context manager, which temporarily modifies the configuration settings. It ensures that the context manager correctly applies and reverts changes to the configuration settings, and that nested context managers can override or revert changes.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function asserts that the initial configuration is as expected.
    - It tests that using the context manager without entering it does not affect the configuration.
    - It
    """

    assert get_config() == {'assume_finite': False, 'working_memory': 1024,
                            'print_changed_only': False}

    # Not using as a context manager affects nothing
    config_context(assume_finite=True)
    assert get_config()['assume_finite'] is False

    with config_context(assume_finite=True):
        assert get_config() == {'assume_finite': True, 'working_memory': 1024,
                                'print_changed_only': False}
    assert get_config()['assume_finite'] is False

    with config_context(assume_finite=True):
        with config_context(assume_finite=None):
            assert get_config()['assume_finite'] is True

        assert get_config()['assume_finite'] is True

        with config_context(assume_finite=False):
            assert get_config()['assume_finite'] is False

            with config_context(assume_finite=None):
                assert get_config()['assume_finite'] is False

                # global setting will not be retained outside of context that
                # did not modify this setting
                set_config(assume_finite=True)
                assert get_config()['assume_finite'] is True

            assert get_config()['assume_finite'] is False

        assert get_config()['assume_finite'] is True

    assert get_config() == {'assume_finite': False, 'working_memory': 1024,
                            'print_changed_only': False}

    # No positional arguments
    assert_raises(TypeError, config_context, True)
    # No unknown arguments
    assert_raises(TypeError, config_context(do_something_else=True).__enter__)


def test_config_context_exception():
    assert get_config()['assume_finite'] is False
    try:
        with config_context(assume_finite=True):
            assert get_config()['assume_finite'] is True
            raise ValueError()
    except ValueError:
        pass
    assert get_config()['assume_finite'] is False


def test_set_config():
    """
    Set or reset the configuration of the library.
    
    Parameters:
    assume_finite (bool, optional): If True, assume that the input data is finite. If None, reset to the default value (False).
    
    Returns:
    None: This function does not return anything. It modifies the configuration in-place.
    
    Raises:
    TypeError: If an unknown argument is provided.
    
    This function allows you to set or reset the configuration of the library. It can be used to control how the library handles certain aspects of
    """

    assert get_config()['assume_finite'] is False
    set_config(assume_finite=None)
    assert get_config()['assume_finite'] is False
    set_config(assume_finite=True)
    assert get_config()['assume_finite'] is True
    set_config(assume_finite=None)
    assert get_config()['assume_finite'] is True
    set_config(assume_finite=False)
    assert get_config()['assume_finite'] is False

    # No unknown arguments
    assert_raises(TypeError, set_config, do_something_else=True)
