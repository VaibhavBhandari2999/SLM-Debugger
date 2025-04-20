import pytest
from _pytest.main import ExitCode


def test_version(testdir, pytestconfig):
    """
    Tests the version information of the pytest framework.
    
    This function runs pytest with the `--version` flag and checks the output for the correct version information and the presence of imported modules. It also verifies if any setuptools registered plugins are listed in the output.
    
    Parameters:
    - testdir (pytest.Testdir): The test directory fixture provided by pytest.
    - pytestconfig (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: The function asserts that the pytest version is correct and that the expected information is
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
    
    This function creates a pytest configuration with an optional hook implementation. The hook is expected to be optional, meaning it can be omitted without causing an error. The function verifies that the test execution does not fail when the optional hook is not provided.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object used to create and run tests.
    
    Returns:
    None: The function asserts that the test execution returns `ExitCode.NO_TESTS_COLLECT
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
    """
    Test the pytest debug mode.
    
    This function sets the environment variable `PYTEST_DEBUG` to '1' and runs pytest subprocess. It checks if the test run results in `NO_TESTS_COLLECTED` exit code and verifies that the stderr output matches the expected lines.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest test directory fixture.
    - monkeypatch (pytest.MonkeyPatch): A pytest monkeypatch fixture to modify environment variables.
    
    Returns:
    - None: The function asserts the expected behavior
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
