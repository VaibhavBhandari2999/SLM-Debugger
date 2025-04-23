import inspect
from unittest import mock

import pytest
from _pytest import deprecated
from _pytest import nodes


@pytest.mark.filterwarnings("default")
def test_resultlog_is_deprecated(testdir):
    """
    Tests the deprecation warning for the `--result-log` option in pytest.
    
    This function checks that the `--result-log` option is deprecated and emits a warning when used. It also verifies that a deprecation message is shown when the option is used with the `--help` flag. Additionally, it ensures that a detailed deprecation message is displayed when running a test with the `--result-log` option.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest test directory fixture.
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
    """
    Function to assert that no print logs are emitted during test execution.
    
    Args:
    testdir (pytest.Testdir): The pytest test directory object.
    args (list): List of arguments to pass to pytest.
    
    Returns:
    None: The function asserts that no print logs are emitted and raises an error if any are found.
    
    Deprecated:
    --no-print-logs is deprecated and scheduled for removal in pytest 6.0. Please use --show-capture instead.
    """

    result = testdir.runpytest(*args)
    result.stdout.fnmatch_lines(
        [
            "*--no-print-logs is deprecated and scheduled for removal in pytest 6.0*",
            "*Please use --show-capture instead.*",
        ]
    )


@pytest.mark.filterwarnings("default")
def test_noprintlogs_is_deprecated_cmdline(testdir):
    testdir.makepyfile(
        """
        def test_foo():
            pass
        """
    )

    assert_no_print_logs(testdir, ("--no-print-logs",))


@pytest.mark.filterwarnings("default")
def test_noprintlogs_is_deprecated_ini(testdir):
    """
    Tests that the `test_noprintlogs_is_deprecated_ini` function correctly configures pytest to disable log printing and runs a test without printing logs.
    
    Parameters:
    testdir (pytest.Testdir): Pytest test directory fixture.
    
    Returns:
    None: The function asserts that no log prints occur during the test.
    """

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
    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match="The `_fillfuncargs` function is deprecated",
    ):
        pytest._fillfuncargs(mock.Mock())
