import re
import sys
import warnings
from pathlib import Path
from unittest import mock

import pytest
from _pytest import deprecated
from _pytest.compat import legacy_path
from _pytest.pytester import Pytester
from pytest import PytestDeprecationWarning


@pytest.mark.parametrize("attribute", pytest.collect.__all__)  # type: ignore
# false positive due to dynamic attribute
def test_pytest_collect_module_deprecated(attribute) -> None:
    with pytest.warns(DeprecationWarning, match=attribute):
        getattr(pytest.collect, attribute)


@pytest.mark.parametrize("plugin", sorted(deprecated.DEPRECATED_EXTERNAL_PLUGINS))
@pytest.mark.filterwarnings("default")
def test_external_plugins_integrated(pytester: Pytester, plugin) -> None:
    """
    Test the integration of external plugins.
    
    This function checks if an external plugin can be integrated with the pytest framework. It inserts the plugin into the system path and creates a test file for the plugin. If the plugin is not integrated correctly, a PytestConfigWarning will be issued.
    
    Parameters:
    pytester (Pytester): A fixture that provides access to Pytester functionalities.
    plugin (str): The name of the plugin to be tested.
    
    Returns:
    None: This function does not return any
    """

    pytester.syspathinsert()
    pytester.makepyfile(**{plugin: ""})

    with pytest.warns(pytest.PytestConfigWarning):
        pytester.parseconfig("-p", plugin)


def test_fillfuncargs_is_deprecated() -> None:
    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match=re.escape(
            "pytest._fillfuncargs() is deprecated, use "
            "function._request._fillfixtures() instead if you cannot avoid reaching into internals."
        ),
    ):
        pytest._fillfuncargs(mock.Mock())


def test_fillfixtures_is_deprecated() -> None:
    import _pytest.fixtures

    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match=re.escape(
            "_pytest.fixtures.fillfixtures() is deprecated, use "
            "function._request._fillfixtures() instead if you cannot avoid reaching into internals."
        ),
    ):
        _pytest.fixtures.fillfixtures(mock.Mock())


def test_minus_k_dash_is_deprecated(pytester: Pytester) -> None:
    threepass = pytester.makepyfile(
        test_threepass="""
        def test_one(): assert 1
        def test_two(): assert 1
        def test_three(): assert 1
    """
    )
    result = pytester.runpytest("-k=-test_two", threepass)
    result.stdout.fnmatch_lines(["*The `-k '-expr'` syntax*deprecated*"])


def test_minus_k_colon_is_deprecated(pytester: Pytester) -> None:
    """
    Test the deprecation warning for the `-k 'expr:'` syntax in pytest.
    
    This function checks that pytest correctly emits a deprecation warning when the `-k 'expr:'` syntax is used.
    
    Args:
    pytester (Pytester): A pytest fixture for creating and running tests.
    
    Returns:
    None: The function asserts that the deprecation warning is emitted.
    """

    threepass = pytester.makepyfile(
        test_threepass="""
        def test_one(): assert 1
        def test_two(): assert 1
        def test_three(): assert 1
    """
    )
    result = pytester.runpytest("-k", "test_two:", threepass)
    result.stdout.fnmatch_lines(["*The `-k 'expr:'` syntax*deprecated*"])


def test_fscollector_gethookproxy_isinitpath(pytester: Pytester) -> None:
    module = pytester.getmodulecol(
        """
        def test_foo(): pass
        """,
        withinit=True,
    )
    assert isinstance(module, pytest.Module)
    package = module.parent
    assert isinstance(package, pytest.Package)

    with pytest.warns(pytest.PytestDeprecationWarning, match="gethookproxy"):
        package.gethookproxy(pytester.path)

    with pytest.warns(pytest.PytestDeprecationWarning, match="isinitpath"):
        package.isinitpath(pytester.path)

    # The methods on Session are *not* deprecated.
    session = module.session
    with warnings.catch_warnings(record=True) as rec:
        session.gethookproxy(pytester.path)
        session.isinitpath(pytester.path)
    assert len(rec) == 0


def test_strict_option_is_deprecated(pytester: Pytester) -> None:
    """--strict is a deprecated alias to --strict-markers (#7530)."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.unknown
        def test_foo(): pass
        """
    )
    result = pytester.runpytest("--strict")
    result.stdout.fnmatch_lines(
        [
            "'unknown' not found in `markers` configuration option",
            "*PytestRemovedIn8Warning: The --strict option is deprecated, use --strict-markers instead.",
        ]
    )


def test_yield_fixture_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match=r"yield_fixture is deprecated"):

        @pytest.yield_fixture
        def fix():
            assert False


def test_private_is_deprecated() -> None:
    """
    Tests for the private `__init__` method in the `PrivateInit` class.
    
    This function checks that the `__init__` method of the `PrivateInit` class raises a `pytest.PytestDeprecationWarning` when the `_ispytest` keyword argument is not set to `True`. The `__init__` method takes two parameters: `foo` (an integer) and `_ispytest` (a boolean with a default value of `False`).
    
    Key Parameters
    """

    class PrivateInit:
        def __init__(self, foo: int, *, _ispytest: bool = False) -> None:
            deprecated.check_ispytest(_ispytest)

    with pytest.warns(
        pytest.PytestDeprecationWarning, match="private pytest class or function"
    ):
        PrivateInit(10)

    # Doesn't warn.
    PrivateInit(10, _ispytest=True)


def test_raising_unittest_skiptest_during_collection_is_deprecated(
    pytester: Pytester,
) -> None:
    pytester.makepyfile(
        """
        import unittest
        raise unittest.SkipTest()
        """
    )
    result = pytester.runpytest()
    result.stdout.fnmatch_lines(
        [
            "*PytestRemovedIn8Warning: Raising unittest.SkipTest*",
        ]
    )


@pytest.mark.parametrize("hooktype", ["hook", "ihook"])
def test_hookproxy_warnings_for_fspath(tmp_path, hooktype, request):
    """
    Tests the warnings generated when using `path` and `fspath` arguments in `pytest_ignore_collect` hook.
    
    This function checks for deprecation warnings when using `path` and `fspath` arguments in the `pytest_ignore_collect` hook. It ensures that the correct warning is raised and that the warning message matches the expected pattern. The function also verifies that passing different paths for `path` and `fspath` arguments raises a `ValueError`.
    
    Parameters:
    - tmp_path (pathlib
    """

    path = legacy_path(tmp_path)

    PATH_WARN_MATCH = r".*path: py\.path\.local\) argument is deprecated, please use \(fspath: pathlib\.Path.*"
    if hooktype == "ihook":
        hooks = request.node.ihook
    else:
        hooks = request.config.hook

    with pytest.warns(PytestDeprecationWarning, match=PATH_WARN_MATCH) as r:
        l1 = sys._getframe().f_lineno
        hooks.pytest_ignore_collect(config=request.config, path=path, fspath=tmp_path)
        l2 = sys._getframe().f_lineno

    (record,) = r
    assert record.filename == __file__
    assert l1 < record.lineno < l2

    hooks.pytest_ignore_collect(config=request.config, fspath=tmp_path)

    # Passing entirely *different* paths is an outright error.
    with pytest.raises(ValueError, match=r"path.*fspath.*need to be equal"):
        with pytest.warns(PytestDeprecationWarning, match=PATH_WARN_MATCH) as r:
            hooks.pytest_ignore_collect(
                config=request.config, path=path, fspath=Path("/bla/bla")
            )


def test_warns_none_is_deprecated():
    with pytest.warns(
        PytestDeprecationWarning,
        match=re.escape(
            "Passing None to catch any warning has been deprecated, pass no arguments instead:\n "
            "Replace pytest.warns(None) by simply pytest.warns()."
        ),
    ):
        with pytest.warns(None):  # type: ignore[call-overload]
            pass


class TestSkipMsgArgumentDeprecated:
    def test_skip_with_msg_is_deprecated(self, pytester: Pytester) -> None:
        p = pytester.makepyfile(
            """
            import pytest

            def test_skipping_msg():
                pytest.skip(msg="skippedmsg")
            """
        )
        result = pytester.runpytest(p)
        result.stdout.fnmatch_lines(
            [
                "*PytestRemovedIn8Warning: pytest.skip(msg=...) is now deprecated, "
                "use pytest.skip(reason=...) instead",
                '*pytest.skip(msg="skippedmsg")*',
            ]
        )
        result.assert_outcomes(skipped=1, warnings=1)

    def test_fail_with_msg_is_deprecated(self, pytester: Pytester) -> None:
        """
        Tests the deprecation warning for the `pytest.fail(msg=...)` function.
        
        This function creates a test file with a failing test that uses `pytest.fail(msg="failedmsg")`. It then runs pytest on this file and checks for the expected deprecation warning. The test ensures that the warning is raised and that the test fails as expected.
        
        Parameters:
        - pytester (Pytester): A fixture provided by `pytest` for creating and running test files.
        
        Returns:
        - None: The function
        """

        p = pytester.makepyfile(
            """
            import pytest

            def test_failing_msg():
                pytest.fail(msg="failedmsg")
            """
        )
        result = pytester.runpytest(p)
        result.stdout.fnmatch_lines(
            [
                "*PytestRemovedIn8Warning: pytest.fail(msg=...) is now deprecated, "
                "use pytest.fail(reason=...) instead",
                '*pytest.fail(msg="failedmsg")',
            ]
        )
        result.assert_outcomes(failed=1, warnings=1)

    def test_exit_with_msg_is_deprecated(self, pytester: Pytester) -> None:
        p = pytester.makepyfile(
            """
            import pytest

            def test_exit_msg():
                pytest.exit(msg="exitmsg")
            """
        )
        result = pytester.runpytest(p)
        result.stdout.fnmatch_lines(
            [
                "*PytestRemovedIn8Warning: pytest.exit(msg=...) is now deprecated, "
                "use pytest.exit(reason=...) instead",
            ]
        )
        result.assert_outcomes(warnings=1)


def test_deprecation_of_cmdline_preparse(pytester: Pytester) -> None:
    pytester.makeconftest(
        """
        def pytest_cmdline_preparse(config, args):
            ...

        """
    )
    result = pytester.runpytest()
    result.stdout.fnmatch_lines(
        [
            "*PytestRemovedIn8Warning: The pytest_cmdline_preparse hook is deprecated*",
            "*Please use pytest_load_initial_conftests hook instead.*",
        ]
    )


def test_node_ctor_fspath_argument_is_deprecated(pytester: Pytester) -> None:
    mod = pytester.getmodulecol("")

    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match=re.escape("The (fspath: py.path.local) argument to File is deprecated."),
    ):
        pytest.File.from_parent(
            parent=mod.parent,
            fspath=legacy_path("bla"),
        )


@pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason="This deprecation can only be emitted on python>=3.7",
)
def test_importing_instance_is_deprecated(pytester: Pytester) -> None:
    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match=re.escape("The pytest.Instance collector type is deprecated"),
    ):
        pytest.Instance

    with pytest.warns(
        pytest.PytestDeprecationWarning,
        match=re.escape("The pytest.Instance collector type is deprecated"),
    ):
        from _pytest.python import Instance  # noqa: F401
e  # noqa: F401
