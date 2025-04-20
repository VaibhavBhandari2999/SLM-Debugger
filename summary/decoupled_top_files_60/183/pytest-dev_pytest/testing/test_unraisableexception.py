import sys

import pytest
from _pytest.pytester import Pytester


if sys.version_info < (3, 8):
    pytest.skip("unraisableexception plugin needs Python>=3.8", allow_module_level=True)


@pytest.mark.filterwarnings("default::pytest.PytestUnraisableExceptionWarning")
def test_unraisable(pytester: Pytester) -> None:
    """
    Tests the handling of unraisable exceptions during object deletion in pytest.
    
    This function creates a test file with a class `BrokenDel` that raises a `ValueError` in its `__del__` method. The test file includes two test functions: `test_it` and `test_2`. When `test_it` is executed, it deletes an instance of `BrokenDel`, which raises an exception. This exception is caught and logged as a warning, ensuring that the test still passes.
    """

    pytester.makepyfile(
        test_it="""
        class BrokenDel:
            def __del__(self):
                raise ValueError("del is broken")

        def test_it():
            obj = BrokenDel()
            del obj

        def test_2(): pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == 0
    assert result.parseoutcomes() == {"passed": 2, "warnings": 1}
    result.stdout.fnmatch_lines(
        [
            "*= warnings summary =*",
            "test_it.py::test_it",
            "  * PytestUnraisableExceptionWarning: Exception ignored in: <function BrokenDel.__del__ at *>",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: del is broken",
            "  ",
            "    warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("default::pytest.PytestUnraisableExceptionWarning")
def test_unraisable_in_setup(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_it="""
        import pytest

        class BrokenDel:
            def __del__(self):
                raise ValueError("del is broken")

        @pytest.fixture
        def broken_del():
            obj = BrokenDel()
            del obj

        def test_it(broken_del): pass
        def test_2(): pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == 0
    assert result.parseoutcomes() == {"passed": 2, "warnings": 1}
    result.stdout.fnmatch_lines(
        [
            "*= warnings summary =*",
            "test_it.py::test_it",
            "  * PytestUnraisableExceptionWarning: Exception ignored in: <function BrokenDel.__del__ at *>",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: del is broken",
            "  ",
            "    warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("default::pytest.PytestUnraisableExceptionWarning")
def test_unraisable_in_teardown(pytester: Pytester) -> None:
    """
    Tests the behavior of a fixture that raises an exception in its teardown phase. The fixture yields control to the test function and then attempts to delete an instance of a custom class `BrokenDel`. This class's `__del__` method is designed to raise a `ValueError`. The test function `test_it` uses this fixture, while `test_2` does not. The test suite is expected to pass all tests but generate a warning due to the unhandled exception in the teardown of the
    """

    pytester.makepyfile(
        test_it="""
        import pytest

        class BrokenDel:
            def __del__(self):
                raise ValueError("del is broken")

        @pytest.fixture
        def broken_del():
            yield
            obj = BrokenDel()
            del obj

        def test_it(broken_del): pass
        def test_2(): pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == 0
    assert result.parseoutcomes() == {"passed": 2, "warnings": 1}
    result.stdout.fnmatch_lines(
        [
            "*= warnings summary =*",
            "test_it.py::test_it",
            "  * PytestUnraisableExceptionWarning: Exception ignored in: <function BrokenDel.__del__ at *>",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: del is broken",
            "  ",
            "    warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("error::pytest.PytestUnraisableExceptionWarning")
def test_unraisable_warning_error(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_it="""
        class BrokenDel:
            def __del__(self) -> None:
                raise ValueError("del is broken")

        def test_it() -> None:
            obj = BrokenDel()
            del obj

        def test_2(): pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    assert result.parseoutcomes() == {"passed": 1, "failed": 1}
