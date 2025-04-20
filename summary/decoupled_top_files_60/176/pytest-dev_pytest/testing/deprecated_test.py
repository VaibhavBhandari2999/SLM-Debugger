import inspect
from unittest import mock

import pytest
from _pytest import deprecated
from _pytest import nodes


@pytest.mark.filterwarnings("default")
def test_resultlog_is_deprecated(testdir):
    """
    Tests the deprecation warning for the `--result-log` option in pytest.
    
    This function checks if the `--result-log` option is correctly marked as deprecated in the help output and if it generates a deprecation warning when used. It also verifies that the warning message includes the correct URL for more information.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object used to run tests.
    
    Output:
    The function checks for specific lines in the output of the pytest run, indicating
    """

    result = testdir.runpytest("--help")
    result.stdout.fnmatch_lines(["*DEPRECATED path for machine-readable result log*"])

    testdir.makepyfile(
        """
        def test():
            pass
    """
    )
    result = testdir.runpytest("--result-log=%s" % testdir.tmpdir.join("result.log"))
    result.stdout.fnmatch_lines(
        [
            "*--result-log is deprecated, please try the new pytest-reportlog plugin.",
            "*See https://docs.pytest.org/en/latest/deprecations.html#result-log-result-log for more information*",
        ]
    )


@pytest.mark.parametrize("attribute", pytest.collect.__all__)  # type: ignore
# false positive due to dynamic attribute
def test_pytest_collect_module_deprecated(attribute):
    with pytest.warns(DeprecationWarning, match=attribute):
        getattr(pytest.collect, attribute)


def test_terminal_reporter_writer_attr(pytestconfig):
    """Check that TerminalReporter._tw is also available as 'writer' (#2984)
    This attribute has been deprecated in 5.4.
    """
    try:
        import xdist  # noqa

        pytest.skip("xdist workers disable the terminal reporter plugin")
    except ImportError:
        pass
    terminal_reporter = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    expected_tw = terminal_reporter._tw

    with pytest.warns(pytest.PytestDeprecationWarning):
        assert terminal_reporter.writer is expected_tw

    with pytest.warns(pytest.PytestDeprecationWarning):
        terminal_reporter.writer = expected_tw

    assert terminal_reporter._tw is expected_tw


@pytest.mark.parametrize("plugin", sorted(deprecated.DEPRECATED_EXTERNAL_PLUGINS))
@pytest.mark.filterwarnings("default")
def test_external_plugins_integrated(testdir, plugin):
    """
    Integrates and tests external plugins in a Pytest environment.
    
    This function is designed to integrate and test external plugins within a Pytest setup. It dynamically imports and configures the specified plugin, and then parses the Pytest configuration with the plugin enabled.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object that provides methods to create and manipulate test files and directories.
    plugin (str): The name of the plugin to be integrated and tested.
    
    Returns:
    None: This
    """

    testdir.syspathinsert()
    testdir.makepyfile(**{plugin: ""})

    with pytest.warns(pytest.PytestConfigWarning):
        testdir.parseconfig("-p", plugin)


@pytest.mark.parametrize("junit_family", [None, "legacy", "xunit2"])
def test_warn_about_imminent_junit_family_default_change(testdir, junit_family):
    """Show a warning if junit_family is not defined and --junitxml is used (#6179)"""
    testdir.makepyfile(
        """
        def test_foo():
            pass
    """
    )
    if junit_family:
        testdir.makeini(
            """
            [pytest]
            junit_family={junit_family}
        """.format(
                junit_family=junit_family
            )
        )

    result = testdir.runpytest("--junit-xml=foo.xml")
    warning_msg = (
        "*PytestDeprecationWarning: The 'junit_family' default value will change*"
    )
    if junit_family:
        result.stdout.no_fnmatch_line(warning_msg)
    else:
        result.stdout.fnmatch_lines([warning_msg])


def test_node_direct_ctor_warning():
    class MockConfig:
        pass

    ms = MockConfig()
    with pytest.warns(
        DeprecationWarning,
        match="Direct construction of .* has been deprecated, please use .*.from_parent.*",
    ) as w:
        nodes.Node(name="test", config=ms, session=ms, nodeid="None")
    assert w[0].lineno == inspect.currentframe().f_lineno - 1
    assert w[0].filename == __file__


def assert_no_print_logs(testdir, args):
    result = testdir.runpytest(*args)
    result.stdout.fnmatch_lines(
        [
            "*--no-print-logs is deprecated and scheduled for removal in pytest 6.0*",
            "*Please use --show-capture instead.*",
        ]
    )


@pytest.mark.filterwarnings("default")
def test_noprintlogs_is_deprecated_cmdline(testdir):
    """
    Tests the `test_noprintlogs_is_deprecated_cmdline` function.
    
    This function checks that the `--no-print-logs` command line option is correctly deprecated. It creates a test file with a simple test function and runs it with the specified command line option. The function asserts that the test runs without printing logs.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory object used to create and run test files.
    
    Returns:
    None: The function asserts that the test
    """

    testdir.makepyfile(
        """
        def test_foo():
            pass
        """
    )

    assert_no_print_logs(testdir, ("--no-print-logs",))


@pytest.mark.filterwarnings("default")
def test_noprintlogs_is_deprecated_ini(testdir):
    testdir.makeini(
        """
        [pytest]
        log_print=False
        """
    )

    testdir.makepyfile(
        """
        def test_foo():
            pass
        """
    )

    assert_no_print_logs(testdir, ())


def test__fillfuncargs_is_deprecated() -> None:
    """
    This function is deprecated and raises a warning when called. It is used to fill function arguments with fixtures. The function takes no parameters and does not return any value.
    
    Warning:
    This function is deprecated and will raise a `PytestDeprecationWarning` when called.
    """

    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match="The `_fillfuncargs` function is deprecated",
    ):
        pytest._fillfuncargs(mock.Mock())
