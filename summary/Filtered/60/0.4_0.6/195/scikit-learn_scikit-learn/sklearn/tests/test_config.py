from sklearn import get_config, set_config, config_context
from sklearn.utils.testing import assert_raises


def test_config_context():
    """
    Test the context manager for configuration settings.
    
    This function tests the `config_context` function, which is used to temporarily
    change the configuration settings within a context manager. The function
    verifies that the configuration settings are correctly modified and restored
    after the context manager exits.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses `assert` statements to check the configuration settings.
    - It tests the context manager with different settings and nested contexts.
    - It ensures
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
    Set the configuration options for the current session.
    
    Parameters:
    - assume_finite (bool, optional): If True, assume that the input data is finite. If None, use the default value (False).
    
    This function sets the configuration options for the current session. It can be used to temporarily change the behavior of the system. The function does not return any value but affects the global configuration.
    
    Note:
    - If `assume_finite` is set to None, the default value (False) is used
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
