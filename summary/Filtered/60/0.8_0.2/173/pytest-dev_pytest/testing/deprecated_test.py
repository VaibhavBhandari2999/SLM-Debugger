import os

import pytest
from _pytest import deprecated
from _pytest.warning_types import PytestDeprecationWarning
from _pytest.warnings import SHOW_PYTEST_WARNINGS_ARG

pytestmark = pytest.mark.pytester_example_path("deprecated")


def test_pytest_setup_cfg_unsupported(testdir):
    testdir.makefile(
        ".cfg",
        setup="""
        [pytest]
        addopts = --verbose
    """,
    )
    with pytest.raises(pytest.fail.Exception):
        testdir.runpytest()


def test_pytest_custom_cfg_unsupported(testdir):
    """
    This function tests the behavior of pytest with a custom configuration file that includes unsupported options. The function creates a custom configuration file and attempts to run pytest with this configuration. If the configuration file contains unsupported options, pytest should raise an exception.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides a temporary directory where the test files and configuration files are created.
    
    Input:
    - A custom configuration file (`custom.cfg`) with the following content:
    ```
    [pytest]
    add
    """

    testdir.makefile(
        ".cfg",
        custom="""
        [pytest]
        addopts = --verbose
    """,
    )
    with pytest.raises(pytest.fail.Exception):
        testdir.runpytest("-c", "custom.cfg")


def test_getfuncargvalue_is_deprecated(request):
    pytest.deprecated_call(request.getfuncargvalue, "tmpdir")


@pytest.mark.filterwarnings("default")
def test_resultlog_is_deprecated(testdir):
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
            "*--result-log is deprecated and scheduled for removal in pytest 6.0*",
            "*See https://docs.pytest.org/en/latest/deprecations.html#result-log-result-log for more information*",
        ]
    )


def test_terminal_reporter_writer_attr(pytestconfig):
    """Check that TerminalReporter._tw is also available as 'writer' (#2984)
    This attribute is planned to be deprecated in 3.4.
    """
    try:
        import xdist  # noqa

        pytest.skip("xdist workers disable the terminal reporter plugin")
    except ImportError:
        pass
    terminal_reporter = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    assert terminal_reporter.writer is terminal_reporter._tw


@pytest.mark.parametrize("plugin", deprecated.DEPRECATED_EXTERNAL_PLUGINS)
@pytest.mark.filterwarnings("default")
def test_external_plugins_integrated(testdir, plugin):
    testdir.syspathinsert()
    testdir.makepyfile(**{plugin: ""})

    with pytest.warns(pytest.PytestConfigWarning):
        testdir.parseconfig("-p", plugin)


def test_raises_message_argument_deprecated():
    with pytest.warns(pytest.PytestDeprecationWarning):
        with pytest.raises(RuntimeError, message="foobar"):
            raise RuntimeError


def test_pytest_plugins_in_non_top_level_conftest_deprecated(testdir):
    from _pytest.deprecated import PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST

    testdir.makepyfile(
        **{
            "subdirectory/conftest.py": """
        pytest_plugins=['capture']
    """
        }
    )
    testdir.makepyfile(
        """
        def test_func():
            pass
    """
    )
    res = testdir.runpytest(SHOW_PYTEST_WARNINGS_ARG)
    assert res.ret == 2
    msg = str(PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST).splitlines()[0]
    res.stdout.fnmatch_lines(
        ["*{msg}*".format(msg=msg), "*subdirectory{sep}conftest.py*".format(sep=os.sep)]
    )


@pytest.mark.parametrize("use_pyargs", [True, False])
def test_pytest_plugins_in_non_top_level_conftest_unsupported_pyargs(
    testdir, use_pyargs
):
    """When using --pyargs, do not emit the warning about non-top-level conftest warnings (#4039, #4044)"""
    from _pytest.deprecated import PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST

    files = {
        "src/pkg/__init__.py": "",
        "src/pkg/conftest.py": "",
        "src/pkg/test_root.py": "def test(): pass",
        "src/pkg/sub/__init__.py": "",
        "src/pkg/sub/conftest.py": "pytest_plugins=['capture']",
        "src/pkg/sub/test_bar.py": "def test(): pass",
    }
    testdir.makepyfile(**files)
    testdir.syspathinsert(testdir.tmpdir.join("src"))

    args = ("--pyargs", "pkg") if use_pyargs else ()
    args += (SHOW_PYTEST_WARNINGS_ARG,)
    res = testdir.runpytest(*args)
    assert res.ret == (0 if use_pyargs else 2)
    msg = str(PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST).splitlines()[0]
    if use_pyargs:
        assert msg not in res.stdout.str()
    else:
        res.stdout.fnmatch_lines(["*{msg}*".format(msg=msg)])


def test_pytest_plugins_in_non_top_level_conftest_unsupported_no_top_level_conftest(
    testdir
):
    from _pytest.deprecated import PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST

    subdirectory = testdir.tmpdir.join("subdirectory")
    subdirectory.mkdir()
    testdir.makeconftest(
        """
        pytest_plugins=['capture']
    """
    )
    testdir.tmpdir.join("conftest.py").move(subdirectory.join("conftest.py"))

    testdir.makepyfile(
        """
        def test_func():
            pass
    """
    )

    res = testdir.runpytest_subprocess()
    assert res.ret == 2
    msg = str(PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST).splitlines()[0]
    res.stdout.fnmatch_lines(
        ["*{msg}*".format(msg=msg), "*subdirectory{sep}conftest.py*".format(sep=os.sep)]
    )


def test_pytest_plugins_in_non_top_level_conftest_unsupported_no_false_positives(
    testdir
):
    from _pytest.deprecated import PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST

    subdirectory = testdir.tmpdir.join("subdirectory")
    subdirectory.mkdir()
    testdir.makeconftest(
        """
        pass
    """
    )
    testdir.tmpdir.join("conftest.py").move(subdirectory.join("conftest.py"))

    testdir.makeconftest(
        """
        import warnings
        warnings.filterwarnings('always', category=DeprecationWarning)
        pytest_plugins=['capture']
    """
    )
    testdir.makepyfile(
        """
        def test_func():
            pass
    """
    )
    res = testdir.runpytest_subprocess()
    assert res.ret == 0
    msg = str(PYTEST_PLUGINS_FROM_NON_TOP_LEVEL_CONFTEST).splitlines()[0]
    assert msg not in res.stdout.str()


def test_fixture_named_request(testdir):
    """
    Test the fixture named 'request' to ensure it raises an error due to being a reserved name for fixtures. The function copies an example test file, runs pytest, and checks if the output matches the expected error message.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides utilities to run pytest in a temporary directory.
    
    Returns:
    - None: The function asserts that the output contains the expected error message and does not indicate successful test runs.
    """

    testdir.copy_example()
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        [
            "*'request' is a reserved name for fixtures and will raise an error in future versions"
        ]
    )


def test_pytest_warns_unknown_kwargs():
    """
    Function: test_pytest_warns_unknown_kwargs
    
    This function is designed to test the behavior of the `pytest.warns` function when it receives unexpected keyword arguments.
    
    Parameters:
    - None
    
    Key Behavior:
    - The function uses `pytest.warns` to issue a `PytestDeprecationWarning` if any unexpected keyword arguments are passed to `pytest.warns`.
    - Specifically, it checks for a warning indicating that `pytest.warns()` received unexpected keyword arguments, such as 'foo'.
    """

    with pytest.warns(
        PytestDeprecationWarning,
        match=r"pytest.warns\(\) got unexpected keyword arguments: \['foo'\]",
    ):
        pytest.warns(UserWarning, foo="hello")
hello")
