import sys

import pytest
from _pytest.pytester import Pytester


if sys.version_info < (3, 8):
    pytest.skip("unraisableexception plugin needs Python>=3.8", allow_module_level=True)


@pytest.mark.filterwarnings("default::pytest.PytestUnraisableExceptionWarning")
def test_unraisable(pytester: Pytester) -> None:
    """
    Tests the handling of unraisable exceptions during object deletion in pytest.
    
    This test function creates a custom object with a broken `__del__` method that raises a `ValueError` when deleted. It then runs a test that deletes this object and another test that does not. The test ensures that the unhandled exception during deletion is properly captured and reported as a warning by pytest.
    
    Key Parameters:
    - `pytester`: A fixture provided by pytest that allows for the creation and execution of test files
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
    Tests the handling of unraisable exceptions during teardown in pytest.
    
    This function creates a test case where a teardown fixture attempts to delete an instance of a custom class `BrokenDel` which raises a `ValueError` in its `__del__` method. The test ensures that the teardown process correctly handles and logs the unraisable exception without failing the test.
    
    Parameters:
    pytester (Pytester): A fixture provided by pytester, used to create and run test files.
    
    Returns:
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
