import pytest
from _pytest.main import ExitCode


def test_version(testdir, pytestconfig):
    """
    Tests the `--version` option of pytest.
    
    This function runs pytest with the `--version` option and checks the output to ensure that the correct version of pytest and its dependencies are displayed. It also verifies that the output includes the version of the pytest package and the path from which it was imported. If any setuptools registered plugins are present, the output will also include information about them.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run the pytest command.
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
    This function is designed to test the behavior of pytest when the environment variable `PYTEST_DEBUG` is set to '1'. It uses the `monkeypatch` fixture to set the environment variable and then runs pytest using `runpytest_subprocess`. The function asserts that the test run results in `ExitCode.NO_TESTS_COLLECTED` and checks that the stderr output matches expected patterns, indicating that the pytest plugin was registered and that the manager plugin was instantiated.
    
    :param testdir: A fixture that provides
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
egistered*", "*manager*PluginManager*"]
    )
