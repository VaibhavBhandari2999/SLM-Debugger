from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest
from _pytest.main import EXIT_NOTESTSCOLLECTED


def test_version(testdir, pytestconfig):
    result = testdir.runpytest("--version")
    assert result.ret == 0
    # p = py.path.local(py.__file__).dirpath()
    result.stderr.fnmatch_lines(
        ["*pytest*{}*imported from*".format(pytest.__version__)]
    )
    if pytestconfig.pluginmanager.list_plugin_distinfo():
        result.stderr.fnmatch_lines(["*setuptools registered plugins:", "*at*"])


def test_help(testdir):
    result = testdir.runpytest("--help")
    assert result.ret == 0
    result.stdout.fnmatch_lines(
        """
        *-v*verbose*
        *setup.cfg*
        *minversion*
        *to see*markers*pytest --markers*
        *to see*fixtures*pytest --fixtures*
    """
    )


def test_hookvalidation_unknown(testdir):
    """
    Tests the pytest hook validation for unknown hooks.
    
    This function runs pytest with a custom conftest file that defines an unknown pytest hook `pytest_hello`. It then checks if pytest correctly identifies and reports the unknown hook.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object used to run tests.
    
    Returns:
    None: The function asserts that pytest correctly identifies the unknown hook and reports it.
    """

    testdir.makeconftest(
        """
        def pytest_hello(xyz):
            pass
    """
    )
    result = testdir.runpytest()
    assert result.ret != 0
    result.stdout.fnmatch_lines(["*unknown hook*pytest_hello*"])


def test_hookvalidation_optional(testdir):
    testdir.makeconftest(
        """
        import pytest
        @pytest.hookimpl(optionalhook=True)
        def pytest_hello(xyz):
            pass
    """
    )
    result = testdir.runpytest()
    assert result.ret == EXIT_NOTESTSCOLLECTED


def test_traceconfig(testdir):
    result = testdir.runpytest("--traceconfig")
    result.stdout.fnmatch_lines(["*using*pytest*py*", "*active plugins*"])


def test_debug(testdir, monkeypatch):
    """
    This function runs pytest with the `--debug` option and checks the exit status and the content of the pytestdebug.log file.
    
    Parameters:
    - testdir: A pytest fixture that provides a temporary directory for testing.
    - monkeypatch: A pytest fixture that allows modifying the system at runtime.
    
    Returns:
    - None: The function asserts the expected behavior and does not return a value.
    
    Key Points:
    - The function runs pytest with the `--debug` option.
    - It checks if the exit status is
    """

    result = testdir.runpytest_subprocess("--debug")
    assert result.ret == EXIT_NOTESTSCOLLECTED
    p = testdir.tmpdir.join("pytestdebug.log")
    assert "pytest_sessionstart" in p.read()


def test_PYTEST_DEBUG(testdir, monkeypatch):
    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
ager*"]
    )
