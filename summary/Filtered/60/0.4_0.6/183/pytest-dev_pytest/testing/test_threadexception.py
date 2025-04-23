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
    """
    Tests the behavior of unhandled exceptions in threads and ensures that pytest correctly identifies and reports them.
    
    This function creates a test case where a thread is started with a target function that raises a ValueError. The main thread then waits for the thread to complete. The test case is designed to check if pytest correctly handles and reports unhandled exceptions in threads.
    
    Parameters:
    pytester (Pytester): A fixture provided by pytest that allows for the creation and execution of test files.
    
    Returns:
    None: The
    """

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
