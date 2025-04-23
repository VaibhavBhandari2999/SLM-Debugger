import pytest
from _pytest.main import ExitCode


def test_version(testdir, pytestconfig):
    """
    This function runs pytest with the --version flag and checks the output for specific patterns.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run pytest.
    - pytestconfig (pytest.Config): A pytest Config object containing configuration details.
    
    Returns:
    - None: The function asserts that the pytest version is correctly displayed and that the output matches expected patterns.
    
    Key Points:
    - The function runs pytest with the --version flag.
    - It checks that the pytest version matches the expected version
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
    
    This function creates a pytest configuration with an optional hook implementation. The hook is expected to be called with a parameter `xyz`. If the hook is not implemented, pytest should return an exit code indicating no tests were collected.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory fixture to create and run the test.
    
    Returns:
    None: The function does not return any value. It runs the test and checks the exit code.
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
    assert result.ret == ExitCode.NO_TESTS_COLLECTED


def test_traceconfig(testdir):
    result = testdir.runpytest("--traceconfig")
    result.stdout.fnmatch_lines(["*using*pytest*py*", "*active plugins*"])


def test_debug(testdir, monkeypatch):
    result = testdir.runpytest_subprocess("--debug")
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    p = testdir.tmpdir.join("pytestdebug.log")
    assert "pytest_sessionstart" in p.read()


def test_PYTEST_DEBUG(testdir, monkeypatch):
    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
