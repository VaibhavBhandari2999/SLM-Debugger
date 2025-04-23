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
        """
        Decorator to ensure that a function is only called in a synchronous context. If an event loop is detected in the current thread, a SynchronousOnlyOperation exception is raised. The function `func` is wrapped to check for the presence of an environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` and to detect if an asyncio event loop is running. If both conditions are not met, the function raises a `SynchronousOnlyOperation` exception. Otherwise, it calls the original function `func` with the
        """

        @functools.wraps(func)
        def inner(*args, **kwargs):
            """
            Detects and handles synchronous-only operations in an asynchronous environment.
            
            This function is designed to be used as a wrapper around synchronous operations that are not safe to run in an asynchronous environment. It checks if the current thread has an active event loop and raises a `SynchronousOnlyOperation` exception if it does. If the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is not set, the function will raise an exception. Otherwise, it will pass the operation to the wrapped function `func`.
            
            Parameters:
            """

            if not os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
                # Detect a running event loop in this thread.
                try:
                    asyncio.get_running_loop()
                except RuntimeError:
                    pass
                else:
                    raise SynchronousOnlyOperation(message)
            # Pass onward.
            return func(*args, **kwargs)
        return inner
    # If the message is actually a function, then be a no-arguments decorator.
    if callable(message):
        func = message
        message = 'You cannot call this from an async context - use a thread or sync_to_async.'
        return decorator(func)
    else:
        return decorator
