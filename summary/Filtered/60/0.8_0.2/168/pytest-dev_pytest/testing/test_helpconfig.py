import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Pytester


def test_version_verbose(pytester: Pytester, pytestconfig, monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD")
    result = pytester.runpytest("--version", "--version")
    assert result.ret == 0
    result.stdout.fnmatch_lines([f"*pytest*{pytest.__version__}*imported from*"])
    if pytestconfig.pluginmanager.list_plugin_distinfo():
        result.stdout.fnmatch_lines(["*setuptools registered plugins:", "*at*"])


def test_version_less_verbose(pytester: Pytester, pytestconfig, monkeypatch) -> None:
    """
    Tests the version output of pytest in a less verbose manner.
    
    This function runs pytest with the `--version` flag and checks if the output matches the expected version string. It uses a monkeypatch to disable plugin auto-loading and captures the test result to ensure the test passes with the correct version information.
    
    Parameters:
    - pytester (Pytester): A fixture provided by pytest for testing pytest itself.
    - pytestconfig: The pytest configuration object.
    - monkeypatch: A fixture that allows modifying the test environment
    """

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
    """
    Validate that an unknown hook function raises an error.
    
    This test ensures that attempting to define a pytest hook function with an unknown name results in an error. The function `pytest_hello` is defined in the conftest file, which is expected to raise an error because `pytest_hello` is not a valid pytest hook.
    
    Key Parameters:
    - `pytester`: A Pytester fixture used to run pytest tests.
    
    Expected Output:
    - The test should fail with an error indicating that the hook function `pytest
    """

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
    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = pytester.runpytest_subprocess()
    assert result.ret == ExitCode.NO_TESTS_COLLECTED
    result.stderr.fnmatch_lines(
        ["*pytest_plugin_registered*", "*manager*PluginManager*"]
    )
