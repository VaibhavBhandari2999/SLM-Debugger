import pytest
from _pytest.config import ExitCode


def test_version_verbose(testdir, pytestconfig):
    """
    This function runs pytest with the `--version` and `--version` options to display the version of pytest and any imported plugins. It uses monkeypatch to remove the environment variable `PYTEST_DISABLE_PLUGIN_AUTOLOAD` to ensure plugins are loaded. The function captures the output and asserts that the exit code is 0, indicating success. It also checks for specific lines in the stderr output to verify the expected version and plugin information are present.
    
    Parameters:
    - testdir (pytest.Testdir): A
    """

    testdir.monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD")
    result = testdir.runpytest("--version", "--version")
    assert result.ret == 0
    result.stderr.fnmatch_lines(
        ["*pytest*{}*imported from*".format(pytest.__version__)]
    )
    if pytestconfig.pluginmanager.list_plugin_distinfo():
        result.stderr.fnmatch_lines(["*setuptools registered plugins:", "*at*"])


def test_version_less_verbose(testdir, pytestconfig):
    testdir.monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD")
    result = testdir.runpytest("--version")
    assert result.ret == 0
    # p = py.path.local(py.__file__).dirpath()
    result.stderr.fnmatch_lines(["pytest {}".format(pytest.__version__)])


def test_help(testdir):
    result = testdir.runpytest("--help")
    assert result.ret == 0
    result.stdout.fnmatch_lines(
        """
          -m MARKEXPR           only run tests matching given mark expression.
                                For example: -m 'mark1 and not mark2'.
        reporting:
          --durations=N *
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


def test_debug(testdir):
    """
    Tests the debug functionality of pytest.
    
    This function runs pytest with the `--debug` flag and checks if the test session does not collect any tests, indicating that pytest is in debug mode. It also verifies that a debug log file is created and contains a specific log message.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run pytest subprocess.
    
    Returns:
    - None: The function asserts that the pytest session does not collect any tests and that the debug log file contains
    """

    result = testdir.runpytest_subprocess("--debug")
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    p = testdir.tmpdir.join("pytestdebug.log")
    assert "pytest_sessionstart" in p.read()


def test_PYTEST_DEBUG(testdir, monkeypatch):
    """
    Test the pytest debug mode.
    
    This function sets the environment variable `PYTEST_DEBUG` to '1' and runs pytest with subprocess. It checks if the test run results in `NO_TESTS_COLLECTED` exit code and verifies that the stderr output matches the expected pattern, indicating that the plugin manager was registered.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
    - monkeypatch (pytest.MonkeyPatch): A pytest fixture that provides monkeypatching
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
