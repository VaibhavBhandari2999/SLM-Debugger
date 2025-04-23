import asyncio
import inspect
import warnings

from asgiref.sync import sync_to_async


class RemovedInNextVersionWarning(DeprecationWarning):
    pass


class RemovedInDjango50Warning(PendingDeprecationWarning):
    pass


class warn_about_renamed_method:
    def __init__(self, class_name, old_method_name, new_method_name, deprecation_warning):
        """
        Initialize a DeprecationWarning object.
        
        This constructor sets up a DeprecationWarning for a specific method in a class.
        
        Parameters:
        class_name (str): The name of the class containing the deprecated method.
        old_method_name (str): The name of the deprecated method.
        new_method_name (str): The name of the new method that should be used instead.
        deprecation_warning (str): The warning message to be displayed when the deprecated method is called.
        
        Attributes:
        class
        """

        self.class_name = class_name
        self.old_method_name = old_method_name
        self.new_method_name = new_method_name
        self.deprecation_warning = deprecation_warning

    def __call__(self, f):
        """
        Wraps a function to issue a deprecation warning.
        
        This function is designed to wrap an existing function `f` that is deprecated. When `f` is called, it will issue a deprecation warning indicating that the function is deprecated and suggesting an alternative function to use. The warning is issued using the `warnings.warn` method.
        
        Args:
        f (function): The deprecated function to be wrapped.
        
        Returns:
        function: A wrapped function that issues a deprecation warning and then calls the original
        """

        def wrapped(*args, **kwargs):
            warnings.warn(
                "`%s.%s` is deprecated, use `%s` instead." %
                (self.class_name, self.old_method_name, self.new_method_name),
                self.deprecation_warning, 2)
            return f(*args, **kwargs)
        return wrapped


class RenameMethodsBase(type):
    """
    Handles the deprecation paths when renaming a method.

    It does the following:
        1) Define the new method if missing and complain about it.
        2) Define the old method if missing.
        3) Complain whenever an old method is called.

    See #15363 for more details.
    """

    renamed_methods = ()

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        for base in inspect.getmro(new_class):
            class_name = base.__name__
            for renamed_method in cls.renamed_methods:
                old_method_name = renamed_method[0]
                old_method = base.__dict__.get(old_method_name)
                new_method_name = renamed_method[1]
                new_method = base.__dict__.get(new_method_name)
                deprecation_warning = renamed_method[2]
                wrapper = warn_about_renamed_method(class_name, *renamed_method)

                # Define the new method if missing and complain about it
                if not new_method and old_method:
                    warnings.warn(
                        "`%s.%s` method should be renamed `%s`." %
                        (class_name, old_method_name, new_method_name),
                        deprecation_warning, 2)
                    setattr(base, new_method_name, old_method)
                    setattr(base, old_method_name, wrapper(old_method))

                # Define the old method as a wrapped call to the new method.
                if not old_method and new_method:
                    setattr(base, old_method_name, wrapper(new_method))

        return new_class


class DeprecationInstanceCheck(type):
    def __instancecheck__(self, instance):
        warnings.warn(
            "`%s` is deprecated, use `%s` instead." % (self.__name__, self.alternative),
            self.deprecation_warning, 2
        )
        return super().__instancecheck__(instance)


class MiddlewareMixin:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        if get_response is None:
            raise ValueError('get_response must be provided.')
        self.get_response = get_response
        self._async_check()
        super().__init__()

    def __repr__(self):
        return '<%s get_response=%s>' % (
            self.__class__.__qualname__,
            getattr(
                self.get_response,
                '__qualname__',
                self.get_response.__class__.__name__,
            ),
        )

    def _async_check(self):
        """
        If get_response is a coroutine function, turns us into async mode so
        a thread is not consumed during a whole request.
        """
        if asyncio.iscoroutinefunction(self.get_response):
            # Mark the class as async-capable, but do the actual switch
            # inside __call__ to avoid swapping out dunder methods
            self._is_coroutine = asyncio.coroutines._is_coroutine

    def __call__(self, request):
        """
        Call the handler for the given request.
        
        This method is used to handle the request. If the get_response method is a coroutine function, it will be called in asynchronous mode. Otherwise, it will be called directly. The method may optionally process the request and response through custom methods before returning the final response.
        
        Parameters:
        request (HttpRequest): The request object containing the client's request details.
        
        Returns:
        HttpResponse: The response object containing the server's response to the client.
        
        Notes:
        - If
        """

        # Exit out to async mode, if needed
        if asyncio.iscoroutinefunction(self.get_response):
            return self.__acall__(request)
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    async def __acall__(self, request):
        """
        Async version of __call__ that is swapped in when an async request
        is running.
        """
        response = None
        if hasattr(self, 'process_request'):
            response = await sync_to_async(
                self.process_request,
                thread_sensitive=True,
            )(request)
        response = response or await self.get_response(request)
        if hasattr(self, 'process_response'):
            response = await sync_to_async(
                self.process_response,
                thread_sensitive=True,
            )(request, response)
        return response
onse
