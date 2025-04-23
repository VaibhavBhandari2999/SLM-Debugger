import builtins
import os
import subprocess
import sys
import textwrap


def test_simple():
    assert 1 + 1 == 2


def test_override_builtins():
    """
    Tests if any built-in Python functions are overridden by the `pylab` module.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If any overridden functions are not in the `ok_to_override` set.
    
    Notes:
    The `ok_to_override` set contains the names of built-in functions that are allowed to be overridden by the `pylab` module. The function checks if any built-in functions are overridden by `pylab` and ensures that the overridden functions are
    """

    import pylab
    ok_to_override = {
        '__name__',
        '__doc__',
        '__package__',
        '__loader__',
        '__spec__',
        'any',
        'all',
        'sum',
        'divmod'
    }
    overridden = {key for key in {*dir(pylab)} & {*dir(builtins)}
                  if getattr(pylab, key) != getattr(builtins, key)}
    assert overridden <= ok_to_override


def test_lazy_imports():
    """
    Test lazy imports of matplotlib.
    
    This function runs a test script that imports various modules from matplotlib and checks that certain modules are not loaded. It ensures that matplotlib uses lazy imports for specific modules.
    
    Parameters:
    None
    
    Returns:
    None
    """

    source = textwrap.dedent("""
    import sys

    import matplotlib.figure
    import matplotlib.backend_bases
    import matplotlib.pyplot

    assert 'matplotlib._tri' not in sys.modules
    assert 'matplotlib._qhull' not in sys.modules
    assert 'matplotlib._contour' not in sys.modules
    assert 'urllib.request' not in sys.modules
    """)

    subprocess.check_call(
        [sys.executable, '-c', source],
        env={**os.environ, "MPLBACKEND": "", "MATPLOTLIBRC": os.devnull})
