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
    """
    Tests the help functionality of pytest.
    
    This function runs pytest with the `--help` option and checks the output to ensure that specific help messages are present. It verifies that the help output includes verbose mode, configuration file paths, minimum version information, and instructions for viewing available markers and fixtures.
    
    Parameters:
    testdir (pytest.Testdir): A pytest Testdir object representing the test directory.
    
    Returns:
    None: The function asserts that the help output contains the expected messages. If any of the expected
    """

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
    This function tests the validation of unknown hooks in pytest. It creates a custom pytest hook with an unknown parameter 'xyz' and runs pytest to check for an error related to the unknown hook.
    
    Key Parameters:
    - testdir: A pytest fixture that provides a temporary directory for testing.
    
    The function does not return any value but prints the output of pytest to the console. If the hook is correctly identified as unknown, the function will exit with a non-zero status code and print a message indicating the unknown hook
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
    result = testdir.runpytest_subprocess("--debug")
    assert result.ret == EXIT_NOTESTSCOLLECTED
    p = testdir.tmpdir.join("pytestdebug.log")
    assert "pytest_sessionstart" in p.read()


def test_PYTEST_DEBUG(testdir, monkeypatch):
    """
    This function is designed to test the behavior of pytest when the environment variable `PYTEST_DEBUG` is set to '1'. It uses the `monkeypatch` fixture to set the environment variable and then runs the pytest subprocess. The function asserts that the test run results in `EXIT_NOTESTSCOLLECTED` and that the stderr output matches specific patterns indicating that the `pytest_plugin_registered` and `manager` PluginManager have been registered.
    
    Parameters:
    - testdir: A fixture that provides a
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
istered*", "*manager*PluginManager*"]
    )
