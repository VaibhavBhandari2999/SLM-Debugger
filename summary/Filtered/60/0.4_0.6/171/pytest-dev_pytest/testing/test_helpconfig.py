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
    
    This function runs pytest with the `--help` option and checks that the output includes specific help messages. It verifies that the help text contains information about verbosity, configuration files, minimum version, and details on how to see available markers and fixtures.
    
    Parameters:
    testdir (pytest.Testdir): A pytest Testdir object that provides utilities to run tests.
    
    Returns:
    None: The function asserts that the output matches the expected help messages and does not return any value
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
    Tests the pytest hook validation for unknown hooks.
    
    This function runs pytest with a custom conftest file that defines an unknown pytest hook `pytest_hello`. It expects pytest to fail and report an error indicating that the hook is unknown.
    
    Parameters:
    testdir (pytest.Testdir): The pytest test directory fixture.
    
    Returns:
    None: The function asserts that pytest fails with an error message indicating an unknown hook.
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
    This function runs pytest with the '--debug' option and checks the exit status and the presence of a debug log file.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run pytest subprocess.
    - monkeypatch (pytest.MonkeyPatch): A pytest MonkeyPatch object used to modify system properties.
    
    Returns:
    - None: The function asserts the exit status and checks the log file for specific content.
    
    Key Points:
    - The function uses `testdir.runpytest_subprocess`
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
