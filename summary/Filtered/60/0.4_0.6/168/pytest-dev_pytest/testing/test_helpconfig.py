import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_version_verbose(pytester: Pytester, pytestconfig, monkeypatch) -> None:
    """
    Tests the `--version` and `--version` options of pytest.
    
    This function runs pytest with the `--version` option twice to check for the correct version and plugin information. It uses a `monkeypatch` to remove the environment variable `PYTEST_DISABLE_PLUGIN_AUTOLOAD` to ensure plugins are loaded. The function asserts that the test exits with a return code of 0 and checks that the output matches expected patterns, including the pytest version and plugin information if available.
    """

    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD")
    result = pytester.runpytest("--version", "--version")
    assert result.ret == 0
    result.stdout.fnmatch_lines([f"*pytest*{pytest.__version__}*imported from*"])
    if pytestconfig.pluginmanager.list_plugin_distinfo():
        result.stdout.fnmatch_lines(["*setuptools registered plugins:", "*at*"])


def test_version_less_verbose(pytester: Pytester, pytestconfig, monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD")
    result = pytester.runpytest("--version")
    assert result.ret == 0
    result.stdout.fnmatch_lines([f"pytest {pytest.__version__}"])


def test_versions():
    """Regression check for the public version attributes in pytest."""
    assert isinstance(pytest.__version__, str)
    assert isinstance(pytest.version_tuple, tuple)


def test_help(pytester: Pytester) -> None:
    result = pytester.runpytest("--help")
    assert result.ret == 0
    result.stdout.fnmatch_lines(
        """
          -m MARKEXPR           Only run tests matching given mark expression. For
                                example: -m 'mark1 and not mark2'.
        Reporting:
          --durations=N *
          -V, --version         Display pytest version and information about plugins.
                                When given twice, also display information about
                                plugins.
        *setup.cfg*
        *minversion*
        *to see*markers*pytest --markers*
        *to see*fixtures*pytest --fixtures*
    """
    )


def test_none_help_param_raises_exception(pytester: Pytester) -> None:
    """Test that a None help param raises a TypeError."""
    pytester.makeconftest(
        """
        def pytest_addoption(parser):
            parser.addini("test_ini", None, default=True, type="bool")
    """
    )
    result = pytester.runpytest("--help")
    result.stderr.fnmatch_lines(
        ["*TypeError: help argument cannot be None for test_ini*"]
    )


def test_empty_help_param(pytester: Pytester) -> None:
    """Test that an empty help param is displayed correctly."""
    pytester.makeconftest(
        """
        def pytest_addoption(parser):
            parser.addini("test_ini", "", default=True, type="bool")
    """
    )
    result = pytester.runpytest("--help")
    assert result.ret == 0
    lines = [
        "  required_plugins (args):",
        "                        Plugins that must be present for pytest to run*",
        "  test_ini (bool):*",
        "Environment variables:",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)


def test_hookvalidation_unknown(pytester: Pytester) -> None:
    pytester.makeconftest(
        """
        def pytest_hello(xyz):
            pass
    """
    )
    result = pytester.runpytest()
    assert result.ret != 0
    result.stdout.fnmatch_lines(["*unknown hook*pytest_hello*"])


def test_hookvalidation_optional(pytester: Pytester) -> None:
    pytester.makeconftest(
        """
        import pytest
        @pytest.hookimpl(optionalhook=True)
        def pytest_hello(xyz):
            pass
    """
    )
    result = pytester.runpytest()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED


def test_traceconfig(pytester: Pytester) -> None:
    result = pytester.runpytest("--traceconfig")
    result.stdout.fnmatch_lines(["*using*pytest*", "*active plugins*"])


def test_debug(pytester: Pytester) -> None:
    result = pytester.runpytest_subprocess("--debug")
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    p = pytester.path.joinpath("pytestdebug.log")
    assert "pytest_sessionstart" in p.read_text("utf-8")


def test_PYTEST_DEBUG(pytester: Pytester, monkeypatch) -> None:
    """
    Test the pytest debug mode.
    
    This function sets the environment variable `PYTEST_DEBUG` to '1' and runs pytest with subprocess. It then checks if the test run resulted in `NO_TESTS_COLLECTED` and verifies that the stderr output matches the expected pattern.
    
    Parameters:
    pytester (Pytester): A fixture that provides methods to run pytest and manipulate test environments.
    monkeypatch (MonkeyPatch): A fixture that allows changing the system's environment variables and attributes of objects during the test
    """

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = pytester.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
