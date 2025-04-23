import sys
import traceback
import warnings
from types import TracebackType
from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional
from typing import Type

import pytest


# Copied from cpython/Lib/test/support/__init__.py, with modifications.
class catch_unraisable_exception:
    """Context manager catching unraisable exception using sys.unraisablehook.

    Storing the exception value (cm.unraisable.exc_value) creates a reference
    cycle. The reference cycle is broken explicitly when the context manager
    exits.

    Storing the object (cm.unraisable.object) can resurrect it if it is set to
    an object which is being finalized. Exiting the context manager clears the
    stored object.

    Usage:
        with catch_unraisable_exception() as cm:
            # code creating an "unraisable exception"
            ...
            # check the unraisable exception: use cm.unraisable
            ...
        # cm.unraisable attribute no longer exists at this point
        # (to break a reference cycle)
    """

    def __init__(self) -> None:
        self.unraisable: Optional["sys.UnraisableHookArgs"] = None
        self._old_hook: Optional[Callable[["sys.UnraisableHookArgs"], Any]] = None

    def _hook(self, unraisable: "sys.UnraisableHookArgs") -> None:
        # Storing unraisable.object can resurrect an object which is being
        # finalized. Storing unraisable.exc_value creates a reference cycle.
        self.unraisable = unraisable

    def __enter__(self) -> "catch_unraisable_exception":
        self._old_hook = sys.unraisablehook
        sys.unraisablehook = self._hook
        return self

    def __exit__(
        """
        Exit the context manager, restoring the previous unraisable hook.
        
        Parameters:
        exc_type (Optional[Type[BaseException]]): The exception type, if any.
        exc_val (Optional[BaseException]): The exception instance, if any.
        exc_tb (Optional[TracebackType]): The traceback, if any.
        
        This method is called when exiting the context manager. It restores the previous unraisable hook using the stored old hook and clears the unraisable attribute.
        """

        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        assert self._old_hook is not None
        sys.unraisablehook = self._old_hook
        self._old_hook = None
        del self.unraisable


def unraisable_exception_runtest_hook() -> Generator[None, None, None]:
    """
    Hook function to handle unraisable exceptions during test execution.
    
    This function captures unraisable exceptions that occur during test execution and issues a warning with detailed information about the exception.
    
    Yields:
    None: This function does not yield any values but captures unraisable exceptions.
    
    Raises:
    pytest.PytestUnraisableExceptionWarning: A warning is raised with a detailed message about the unraisable exception.
    
    Usage:
    This function should be used as a hook in a testing framework to ensure
    """

    with catch_unraisable_exception() as cm:
        yield
        if cm.unraisable:
            if cm.unraisable.err_msg is not None:
                err_msg = cm.unraisable.err_msg
            else:
                err_msg = "Exception ignored in"
            msg = f"{err_msg}: {cm.unraisable.object!r}\n\n"
            msg += "".join(
                traceback.format_exception(
                    cm.unraisable.exc_type,
                    cm.unraisable.exc_value,
                    cm.unraisable.exc_traceback,
                )
            )
            warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup() -> Generator[None, None, None]:
    yield from unraisable_exception_runtest_hook()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call() -> Generator[None, None, None]:
    yield from unraisable_exception_runtest_hook()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown() -> Generator[None, None, None]:
    yield from unraisable_exception_runtest_hook()
