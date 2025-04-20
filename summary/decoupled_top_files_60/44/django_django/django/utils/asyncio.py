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
            Detects and raises an exception if the provided function is called in an asynchronous context when Django does not allow unsafe operations.
            
            Parameters:
            *args: Variable length argument list to be passed to the function.
            **kwargs: Arbitrary keyword arguments to be passed to the function.
            
            Returns:
            The result of the function call if no asynchronous context is detected.
            
            Raises:
            SynchronousOnlyOperation: If the function is called in an asynchronous context and Django does not allow unsafe operations.
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
