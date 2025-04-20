import re
import sys
import warnings
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
    
    This function checks if an external plugin can be integrated with the pytest framework.
    
    Parameters:
    pytester (Pytester): A pytester fixture for creating and testing test files.
    plugin (str): The name of the plugin to be tested.
    
    This function does not return any value but raises a warning if the plugin integration fails.
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
    Tests the deprecation warning for the `-k 'expr:'` syntax in pytest.
    
    This function runs a pytest test with a specific keyword argument to check if the deprecation warning is correctly issued for the deprecated `-k 'expr:'` syntax.
    
    Parameters:
    pytester (Pytester): A fixture provided by pytester to run pytest tests.
    
    Returns:
    None: The function asserts that the deprecation warning is issued.
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
            "*PytestDeprecationWarning: The --strict option is deprecated, use --strict-markers instead.",
        ]
    )


def test_yield_fixture_is_deprecated() -> None:
    """
    This function tests the deprecation of the `yield_fixture` in pytest. It uses a context manager to warn about the deprecation of `yield_fixture`. The function defines a fixture `fix` that asserts False. The function does not take any parameters and does not return any value. It is expected to raise a DeprecationWarning when the fixture is used.
    
    Key Points:
    - Utilizes `pytest.warns` to capture and assert the deprecation warning.
    - Defines a fixture `fix`
    """

    with pytest.warns(DeprecationWarning, match=r"yield_fixture is deprecated"):

        @pytest.yield_fixture
        def fix():
            assert False


def test_private_is_deprecated() -> None:
    """
    Tests for the `PrivateInit` class.
    
    This function checks the behavior of the `PrivateInit` class, which is deprecated when the `_ispytest` parameter is not set to `True`. The function raises a `pytest.PytestDeprecationWarning` if `_ispytest` is not set to `True`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    pytest.PytestDeprecationWarning: When `_ispytest` is not set to `True`.
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
            "*PytestDeprecationWarning: Raising unittest.SkipTest*",
        ]
    )


@pytest.mark.parametrize("hooktype", ["hook", "ihook"])
def test_hookproxy_warnings_for_fspath(tmp_path, hooktype, request):
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
ns(None) by simply pytest.warns()."
        ),
    ):
        with pytest.warns(None):  # type: ignore[call-overload]
            pass
