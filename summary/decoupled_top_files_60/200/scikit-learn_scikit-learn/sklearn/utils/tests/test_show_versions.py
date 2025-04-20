
from sklearn.utils._show_versions import _get_sys_info
from sklearn.utils._show_versions import _get_deps_info
from sklearn.utils._show_versions import show_versions
from sklearn.utils.testing import ignore_warnings


def test_get_sys_info():
    sys_info = _get_sys_info()

    assert 'python' in sys_info
    assert 'executable' in sys_info
    assert 'machine' in sys_info


def test_get_deps_info():
    """
    Tests the `_get_deps_info` function to ensure it correctly retrieves and returns information about installed dependencies.
    
    This function does not take any parameters or keyword arguments. It internally uses a context manager to ignore any warnings that may occur during the retrieval of dependency information. The function asserts that the returned dictionary contains keys for several important dependencies, including pip, setuptools, sklearn, numpy, scipy, Cython, pandas, matplotlib, and joblib. If any of these dependencies are missing from the returned dictionary, the
    """

    with ignore_warnings():
        deps_info = _get_deps_info()

    assert 'pip' in deps_info
    assert 'setuptools' in deps_info
    assert 'sklearn' in deps_info
    assert 'numpy' in deps_info
    assert 'scipy' in deps_info
    assert 'Cython' in deps_info
    assert 'pandas' in deps_info
    assert 'matplotlib' in deps_info
    assert 'joblib' in deps_info


def test_show_versions(capsys):
    """
    Show versions of key libraries and Python environment.
    
    This function prints the versions of key libraries and the Python environment
    that are currently active. It is useful for diagnosing compatibility issues
    and for logging the environment in which code is run.
    
    No parameters or keywords are required.
    
    The function outputs to the standard output and captures any printed output
    for further processing if needed.
    """

    with ignore_warnings():
        show_versions()
        out, err = capsys.readouterr()

    assert 'python' in out
    assert 'numpy' in out
