from contextlib import contextmanager
import gc
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

import pytest

import matplotlib as mpl
from matplotlib import pyplot as plt, style
from matplotlib.style.core import USER_LIBRARY_PATHS, STYLE_EXTENSION


PARAM = 'image.cmap'
VALUE = 'pink'
DUMMY_SETTINGS = {PARAM: VALUE}


@contextmanager
def temp_style(style_name, settings=None):
    """Context manager to create a style sheet in a temporary directory."""
    if not settings:
        settings = DUMMY_SETTINGS
    temp_file = '%s.%s' % (style_name, STYLE_EXTENSION)
    try:
        with TemporaryDirectory() as tmpdir:
            # Write style settings to file in the tmpdir.
            Path(tmpdir, temp_file).write_text(
                "\n".join("{}: {}".format(k, v) for k, v in settings.items()))
            # Add tmpdir to style path and reload so we can access this style.
            USER_LIBRARY_PATHS.append(tmpdir)
            style.reload_library()
            yield
    finally:
        style.reload_library()


def test_invalid_rc_warning_includes_filename(caplog):
    """
    Test that the warning message for invalid rc files includes the filename.
    
    This function checks if the warning message generated when an invalid rc file
    is encountered includes the filename of the rc file. The function uses a
    temporary style configuration to trigger the warning and asserts that exactly
    one warning is logged, and the filename is included in the warning message.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): A pytest fixture for capturing log messages.
    
    Returns:
    None: The function asserts that the warning message
    """

    SETTINGS = {'foo': 'bar'}
    basename = 'basename'
    with temp_style(basename, SETTINGS):
        # style.reload_library() in temp_style() triggers the warning
        pass
    assert (len(caplog.records) == 1
            and basename in caplog.records[0].getMessage())


def test_available():
    with temp_style('_test_', DUMMY_SETTINGS):
        assert '_test_' in style.available


def test_use():
    """
    Set a temporary style context for the matplotlib plot.
    
    This function temporarily changes the matplotlib style to 'test' with the specified DUMMY_SETTINGS and ensures that the parameter PARAM is set to VALUE. The changes are automatically reverted after the context is exited.
    
    Parameters:
    None
    
    Keywords:
    None
    
    Returns:
    None
    
    Raises:
    None
    """

    mpl.rcParams[PARAM] = 'gray'
    with temp_style('test', DUMMY_SETTINGS):
        with style.context('test'):
            assert mpl.rcParams[PARAM] == VALUE


def test_use_url(tmpdir):
    path = Path(tmpdir, 'file')
    path.write_text('axes.facecolor: adeade')
    with temp_style('test', DUMMY_SETTINGS):
        url = ('file:'
               + ('///' if sys.platform == 'win32' else '')
               + path.resolve().as_posix())
        with style.context(url):
            assert mpl.rcParams['axes.facecolor'] == "#adeade"


def test_single_path(tmpdir):
    mpl.rcParams[PARAM] = 'gray'
    temp_file = f'text.{STYLE_EXTENSION}'
    path = Path(tmpdir, temp_file)
    path.write_text(f'{PARAM} : {VALUE}')
    with style.context(path):
        assert mpl.rcParams[PARAM] == VALUE
    assert mpl.rcParams[PARAM] == 'gray'


def test_context():
    mpl.rcParams[PARAM] = 'gray'
    with temp_style('test', DUMMY_SETTINGS):
        with style.context('test'):
            assert mpl.rcParams[PARAM] == VALUE
    # Check that this value is reset after the exiting the context.
    assert mpl.rcParams[PARAM] == 'gray'


def test_context_with_dict():
    original_value = 'gray'
    other_value = 'blue'
    mpl.rcParams[PARAM] = original_value
    with style.context({PARAM: other_value}):
        assert mpl.rcParams[PARAM] == other_value
    assert mpl.rcParams[PARAM] == original_value


def test_context_with_dict_after_namedstyle():
    """
    Test the context manager for modifying matplotlib style parameters.
    
    This function checks the behavior of the context manager when a dictionary is used to modify the style parameters after applying a named style. Specifically, it ensures that the parameter value is correctly updated within the context and reverts to its original value outside the context.
    
    Parameters:
    PARAM (str): The parameter name in the matplotlib rcParams to be modified.
    original_value (str): The original value of the parameter in the rcParams.
    other_value (
    """

    # Test dict after style name where dict modifies the same parameter.
    original_value = 'gray'
    other_value = 'blue'
    mpl.rcParams[PARAM] = original_value
    with temp_style('test', DUMMY_SETTINGS):
        with style.context(['test', {PARAM: other_value}]):
            assert mpl.rcParams[PARAM] == other_value
    assert mpl.rcParams[PARAM] == original_value


def test_context_with_dict_before_namedstyle():
    # Test dict before style name where dict modifies the same parameter.
    original_value = 'gray'
    other_value = 'blue'
    mpl.rcParams[PARAM] = original_value
    with temp_style('test', DUMMY_SETTINGS):
        with style.context([{PARAM: other_value}, 'test']):
            assert mpl.rcParams[PARAM] == VALUE
    assert mpl.rcParams[PARAM] == original_value


def test_context_with_union_of_dict_and_namedstyle():
    # Test dict after style name where dict modifies the a different parameter.
    original_value = 'gray'
    other_param = 'text.usetex'
    other_value = True
    d = {other_param: other_value}
    mpl.rcParams[PARAM] = original_value
    mpl.rcParams[other_param] = (not other_value)
    with temp_style('test', DUMMY_SETTINGS):
        with style.context(['test', d]):
            assert mpl.rcParams[PARAM] == VALUE
            assert mpl.rcParams[other_param] == other_value
    assert mpl.rcParams[PARAM] == original_value
    assert mpl.rcParams[other_param] == (not other_value)


def test_context_with_badparam():
    """
    Test context manager with invalid parameter.
    
    This function sets the context for a matplotlib style with a specified parameter value. It then checks if the parameter value is correctly set. After that, it attempts to use an invalid parameter within the context and expects a KeyError to be raised. Finally, it ensures that the parameter value is reset to its original value.
    
    Parameters:
    original_value (str): The original value of the parameter to be set.
    other_value (str): The value to temporarily set the parameter
    """

    original_value = 'gray'
    other_value = 'blue'
    with style.context({PARAM: other_value}):
        assert mpl.rcParams[PARAM] == other_value
        x = style.context({PARAM: original_value, 'badparam': None})
        with pytest.raises(KeyError):
            with x:
                pass
        assert mpl.rcParams[PARAM] == other_value


@pytest.mark.parametrize('equiv_styles',
                         [('mpl20', 'default'),
                          ('mpl15', 'classic')],
                         ids=['mpl20', 'mpl15'])
def test_alias(equiv_styles):
    """
    Test if different style aliases in Matplotlib result in equivalent configurations.
    
    Parameters:
    equiv_styles (list): A list of Matplotlib style names or aliases to be compared.
    
    Returns:
    None: The function does not return any value. It asserts that all provided style aliases result in the same Matplotlib configuration.
    
    This function iterates over a list of Matplotlib style names or aliases. For each style, it temporarily sets the style using `matplotlib.pyplot.style.context` and captures the current Matplotlib configuration using `
    """

    rc_dicts = []
    for sty in equiv_styles:
        with style.context(sty):
            rc_dicts.append(mpl.rcParams.copy())

    rc_base = rc_dicts[0]
    for nm, rc in zip(equiv_styles[1:], rc_dicts[1:]):
        assert rc_base == rc


def test_xkcd_no_cm():
    assert mpl.rcParams["path.sketch"] is None
    plt.xkcd()
    assert mpl.rcParams["path.sketch"] == (1, 100, 2)
    gc.collect()
    assert mpl.rcParams["path.sketch"] == (1, 100, 2)


def test_xkcd_cm():
    """
    Context manager to set the matplotlib style to 'xkcd'.
    
    This context manager temporarily changes the matplotlib configuration to use
    the 'xkcd' style within the context block. It restores the previous configuration
    after the block is exited.
    
    Key Parameters:
    None
    
    Keywords:
    None
    
    Inputs:
    None
    
    Outputs:
    None
    
    Example:
    with plt.xkcd():
    # Code block where the matplotlib style is set to 'xkcd'
    # The style will be
    """

    assert mpl.rcParams["path.sketch"] is None
    with plt.xkcd():
        assert mpl.rcParams["path.sketch"] == (1, 100, 2)
    assert mpl.rcParams["path.sketch"] is None
