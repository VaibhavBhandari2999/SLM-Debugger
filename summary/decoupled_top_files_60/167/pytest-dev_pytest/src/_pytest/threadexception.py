import threading
import traceback
import warnings
from types import TracebackType
from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional
from typing import Type

import pytest


# Copied from cpython/Lib/test/support/threading_helper.py, with modifications.
class catch_threading_exception:
    """Context manager catching threading.Thread exception using
    threading.excepthook.

    Storing exc_value using a custom hook can create a reference cycle. The
    reference cycle is broken explicitly when the context manager exits.

    Storing thread using a custom hook can resurrect it if it is set to an
    object which is being finalized. Exiting the context manager clears the
    stored object.

    Usage:
        with threading_helper.catch_threading_exception() as cm:
            # code spawning a thread which raises an exception
            ...
            # check the thread exception: use cm.args
            ...
        # cm.args attribute no longer exists at this point
        # (to break a reference cycle)
    """

    def __init__(self) -> None:
        self.args: Optional["threading.ExceptHookArgs"] = None
        self._old_hook: Optional[Callable[["threading.ExceptHookArgs"], Any]] = None

    def _hook(self, args: "threading.ExceptHookArgs") -> None:
        self.args = args

    def __enter__(self) -> "catch_threading_exception":
        """
        Enter the context of a `catch_threading_exception` object, which temporarily sets the threading exception hook to capture and handle exceptions thrown in threads.
        
        This method is typically used in a `with` statement to ensure that exceptions in threads are properly captured and handled.
        
        Parameters:
        None
        
        Returns:
        catch_threading_exception: The current instance of `catch_threading_exception` with the modified threading exception hook.
        
        Notes:
        - The original threading exception hook is saved and restored upon exiting the `
        """

        self._old_hook = threading.excepthook
        threading.excepthook = self._hook
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        assert self._old_hook is not None
        threading.excepthook = self._old_hook
        self._old_hook = None
        del self.args


def thread_exception_runtest_hook() -> Generator[None, None, None]:
    """
    Runs a test function in a thread and catches any unhandled exceptions.
    
    This function is a generator that yields control to the test function. If an unhandled exception occurs in the thread, it captures the exception and generates a warning with a detailed traceback. The warning includes the name of the thread where the exception occurred.
    
    Yields:
    None: Control is yielded to the test function.
    
    Raises:
    pytest.PytestUnhandledThreadExceptionWarning: If an unhandled exception is caught in the thread.
    """

    with catch_threading_exception() as cm:
        yield
        if cm.args:
            thread_name = "<unknown>" if cm.args.thread is None else cm.args.thread.name
            msg = f"Exception in thread {thread_name}\n\n"
            msg += "".join(
                traceback.format_exception(
                    cm.args.exc_type,
                    cm.args.exc_value,
                    cm.args.exc_traceback,
                )
            )
            warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_setup() -> Generator[None, None, None]:
    yield from thread_exception_runtest_hook()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call() -> Generator[None, None, None]:
    yield from thread_exception_runtest_hook()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown() -> Generator[None, None, None]:
    yield from thread_exception_runtest_hook()
