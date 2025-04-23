import pytest
from _pytest.main import ExitCode


def test_version(testdir, pytestconfig):
    """
    This function runs pytest with the --version flag and checks the output for correctness.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object.
    - pytestconfig (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: The function asserts the expected output and does not return any value.
    
    Key Points:
    - The function runs pytest with the --version flag.
    - It checks that the pytest version is correctly displayed.
    - It verifies that the pytest version is imported from the expected location
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
    """
    Tests the pytest hook validation for unknown hooks.
    
    This function runs pytest with a custom conftest file that defines an unknown pytest hook `pytest_hello`. The function checks if pytest correctly identifies and reports the unknown hook.
    
    Parameters:
    testdir (pytest.Testdir): Pytest test directory object to run tests in.
    
    Returns:
    None: The function asserts that pytest reports an error for the unknown hook.
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
  ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
