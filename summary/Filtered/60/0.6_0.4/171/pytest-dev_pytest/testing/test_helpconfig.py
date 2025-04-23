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
    
    This function runs pytest with the `--help` option and checks that the output matches the expected lines. It verifies that specific options and markers are correctly displayed in the help output.
    
    Parameters:
    testdir (pytest.Testdir): A pytest Testdir object used to run the test.
    
    Returns:
    None: The function asserts that the output matches the expected lines and does not return any value.
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
    Function to test the pytest debug mode.
    
    This function sets the environment variable `PYTEST_DEBUG` to '1' and runs pytest with subprocess mode. It then checks if the test run results in `EXIT_NOTESTSCOLLECTED` and verifies that the stderr contains specific lines indicating the successful registration of the pytest plugin and the creation of the PluginManager.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run tests.
    - monkeypatch (pytest.MonkeyPatch
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
