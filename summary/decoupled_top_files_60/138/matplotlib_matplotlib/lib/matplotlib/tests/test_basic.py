import builtins
import os
import subprocess
import sys
import textwrap


def test_simple():
    assert 1 + 1 == 2


def test_override_builtins():
    """
    Tests whether any built-in Python functions are overridden by the `pylab` module.
    
    This function checks if any of the built-in Python functions are overridden by the `pylab` module. It allows overriding of certain built-in functions specified in the `ok_to_override` set. The function returns a set of overridden functions that are not in the `ok_to_override` set.
    
    Parameters:
    None
    
    Returns:
    set: A set of built-in functions that are overridden by `pylab`
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
