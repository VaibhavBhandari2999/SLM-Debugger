import asyncio
import functools
import os

from django.core.exceptions import SynchronousOnlyOperation


def async_unsafe(message):
    """
    Decorator to mark functions as async-unsafe. Someone trying to access
    the function while in an async context will get an error message.
    """
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            """
            This function is a wrapper that checks for asynchronous unsafety in a Django environment. It ensures that the provided function `func` is called only when no asynchronous operations are in progress, as indicated by the presence of an active event loop in the current thread. If the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is not set, and an event loop is detected, a `SynchronousOnlyOperation` exception is raised. Otherwise, the function `func` is called with the provided arguments and keyword
            """

            if not os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
                # Detect a running event loop in this thread.
                try:
                    event_loop = asyncio.get_event_loop()
                except RuntimeError:
                    pass
                else:
                    if event_loop.is_running():
                        raise SynchronousOnlyOperation(message)
            # Pass onwards.
            return func(*args, **kwargs)
        return inner
    # If the message is actually a function, then be a no-arguments decorator.
    if callable(message):
        func = message
        message = 'You cannot call this from an async context - use a thread or sync_to_async.'
        return decorator(func)
    else:
        return decorator
