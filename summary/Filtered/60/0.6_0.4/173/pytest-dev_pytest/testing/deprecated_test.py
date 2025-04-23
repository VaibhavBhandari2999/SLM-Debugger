import os

import pytest
from _pytest import deprecated
from _pytest.warning_types import PytestDeprecationWarning
from _pytest.warnings import SHOW_PYTEST_WARNINGS_ARG

pytestmark = pytest.mark.pytester_example_path("deprecated")


def test_pytest_setup_cfg_unsupported(testdir):
    """
    This function tests the setup configuration for pytest using a .cfg file. The function creates a .cfg file with a pytest section that includes addopts to specify command-line options. If the setup is not supported, a pytest fail exception is raised.
    
    Parameters:
    - testdir (pytest.Testdir): The test directory object provided by pytest.
    
    Returns:
    - None: The function directly raises an exception if the setup is not supported.
    
    Usage:
    ```python
    test_pytest_setup_cfg_unsupported(testdir)
    """

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
    """
    Function to test if a pytest.raises context manager raises a specific exception with a given message.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - This function is deprecated and will raise a PytestDeprecationWarning.
    - It uses the pytest.raises context manager to check if a RuntimeError is raised.
    - The 'message' parameter is used to specify the expected error message.
    - A PytestDeprecationWarning is raised to indicate that this usage is deprecated.
    """

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
    """
    Tests for the presence of pytest plugins in non-top level conftest files.
    
    This function checks for the presence of pytest plugins in a non-top level conftest file and ensures that the appropriate deprecation warning is not raised. It involves moving a conftest file to a subdirectory and setting up a test file to run pytest on.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides a temporary directory for testing.
    
    Returns:
    None: The function asserts that the
    """

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
    This function tests a fixture named 'request', which is a reserved name for fixtures and will raise an error in future versions. The function copies an example file, runs pytest, and checks if the output matches the expected error message.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used for running tests and copying example files.
    
    Returns:
    - None: The function does not return anything. It checks the output of pytest for the expected error message.
    """

    testdir.copy_example()
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        [
            "*'request' is a reserved name for fixtures and will raise an error in future versions"
        ]
    )


def test_pytest_warns_unknown_kwargs():
    with pytest.warns(
        PytestDeprecationWarning,
        match=r"pytest.warns\(\) got unexpected keyword arguments: \['foo'\]",
    ):
        pytest.warns(UserWarning, foo="hello")
