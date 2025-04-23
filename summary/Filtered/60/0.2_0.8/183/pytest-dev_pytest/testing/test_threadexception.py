import sys

import pytest
from _pytest.pytester import Pytester


if sys.version_info < (3, 8):
    pytest.skip("threadexception plugin needs Python>=3.8", allow_module_level=True)


@pytest.mark.filterwarnings("default::pytest.PytestUnhandledThreadExceptionWarning")
def test_unhandled_thread_exception(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_it="""
        import threading

        def test_it():
            def oops():
                raise ValueError("Oops")

            t = threading.Thread(target=oops, name="MyThread")
            t.start()
            t.join()

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
            "  * PytestUnhandledThreadExceptionWarning: Exception in thread MyThread",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: Oops",
            "  ",
            "    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("default::pytest.PytestUnhandledThreadExceptionWarning")
def test_unhandled_thread_exception_in_setup(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_it="""
        import threading
        import pytest

        @pytest.fixture
        def threadexc():
            def oops():
                raise ValueError("Oops")
            t = threading.Thread(target=oops, name="MyThread")
            t.start()
            t.join()

        def test_it(threadexc): pass
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
            "  * PytestUnhandledThreadExceptionWarning: Exception in thread MyThread",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: Oops",
            "  ",
            "    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("default::pytest.PytestUnhandledThreadExceptionWarning")
def test_unhandled_thread_exception_in_teardown(pytester: Pytester) -> None:
    """
    Tests the handling of unhandled thread exceptions in the teardown phase of a pytest fixture.
    
    This function creates a fixture that starts a thread which raises an exception. The test function and another test function are defined. The test function uses the fixture, while the other test function does not. The pytester fixture is used to run pytest on the generated test file. The function asserts that the test run completes successfully, with two passed tests and one warning about an unhandled thread exception.
    
    Parameters:
    - pytester
    """

    pytester.makepyfile(
        test_it="""
        import threading
        import pytest

        @pytest.fixture
        def threadexc():
            def oops():
                raise ValueError("Oops")
            yield
            t = threading.Thread(target=oops, name="MyThread")
            t.start()
            t.join()

        def test_it(threadexc): pass
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
            "  * PytestUnhandledThreadExceptionWarning: Exception in thread MyThread",
            "  ",
            "  Traceback (most recent call last):",
            "  ValueError: Oops",
            "  ",
            "    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))",
        ]
    )


@pytest.mark.filterwarnings("error::pytest.PytestUnhandledThreadExceptionWarning")
def test_unhandled_thread_exception_warning_error(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_it="""
        import threading
        import pytest

        def test_it():
            def oops():
                raise ValueError("Oops")
            t = threading.Thread(target=oops, name="MyThread")
            t.start()
            t.join()

        def test_2(): pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    assert result.parseoutcomes() == {"passed": 1, "failed": 1}
