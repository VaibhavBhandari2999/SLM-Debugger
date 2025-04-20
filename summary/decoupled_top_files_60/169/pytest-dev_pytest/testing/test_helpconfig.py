from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest
from _pytest.main import EXIT_NOTESTSCOLLECTED


def test_version(testdir, pytestconfig):
    """
    Tests the `--version` option of pytest.
    
    This function runs pytest with the `--version` option and checks the output to ensure that the correct version of pytest and its dependencies are displayed. It also verifies that the version information is imported from the expected location and that any registered plugins are listed if available.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest test directory fixture.
    - pytestconfig (pytest.PytestConfig): A pytest configuration fixture.
    
    Returns:
    - None: The function
    """

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
    Tests the pytest help output.
    
    This function runs pytest with the `--help` flag and checks the output to ensure that specific options and markers are listed. The function does not take any parameters and returns the result of the pytest run.
    
    :returns: The result of the pytest run.
    :rtype: `pytest.Result`
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
    """
    Tests the pytest hook validation for an optional hook.
    
    This function creates a pytest configuration that defines an optional hook named `pytest_hello`. The hook is marked as optional, meaning it can be omitted without causing an error. The function then runs pytest and checks the exit code to ensure that the test suite can be executed even if the optional hook is not provided.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object used to create and run tests.
    
    Returns:
    None: The function
    """

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
    Test the pytest debug mode.
    
    This function sets the environment variable `PYTEST_DEBUG` to '1' and runs pytest in subprocess mode. It checks if the test execution results in `EXIT_NOTESTSCOLLECTED` and verifies that the stderr output matches the expected lines, indicating that the pytest plugin has been registered and the manager is a PluginManager instance.
    
    Parameters:
    - testdir: pytest fixture for creating and managing test directories.
    - monkeypatch: pytest fixture for modifying the environment or test
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
