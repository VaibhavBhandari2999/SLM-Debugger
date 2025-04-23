import asyncio
import inspect
import warnings

from asgiref.sync import sync_to_async


class RemovedInDjango41Warning(DeprecationWarning):
    pass


class RemovedInDjango50Warning(PendingDeprecationWarning):
    pass


RemovedInNextVersionWarning = RemovedInDjango41Warning


class warn_about_renamed_method:
    def __init__(self, class_name, old_method_name, new_method_name, deprecation_warning):
        """
        Initialize a DeprecationWarning object.
        
        Args:
        class_name (str): The name of the class that contains the deprecated method.
        old_method_name (str): The name of the deprecated method.
        new_method_name (str): The name of the new method that should be used instead.
        deprecation_warning (str): The warning message to be displayed when the deprecated method is called.
        
        Returns:
        None: This function does not return any value.
        """

        self.class_name = class_name
        self.old_method_name = old_method_name
        self.new_method_name = new_method_name
        self.deprecation_warning = deprecation_warning

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            """
            This function is a wrapper that deprecates the use of a specific method in favor of a new one. It issues a warning when the deprecated method is called, directing the user to the new method.
            
            Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
            Returns:
            The result of calling the function `f` with the provided arguments and keyword arguments.
            """

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
        """
        This function is a metaclass method that dynamically modifies a new class during its creation. It iterates through the method resolution order (MRO) of the new class and renames methods based on predefined rules. For each base class in the MRO, it checks for methods that need renaming and wraps them with a warning mechanism. If a method is missing in the new class but exists in the base class, it either warns about the missing method or renames it. If a method is present in
        """

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
        """
        Method: __instancecheck__
        
        This method is a deprecated alias for a more modern method and is intended to be used for checking if an instance is an instance of a given class or of a subclass thereof.
        
        Parameters:
        - instance: The object to check.
        
        Returns:
        - A boolean value indicating whether the given instance is an instance of the class or a subclass thereof.
        
        Deprecation Notice:
        This method is deprecated and will be removed in future versions. Users are advised to use the `alternative`
        """

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
        """
        This function returns a string representation of the object. The string includes the class name and the name of the method used to get the response. If the method has a `__qualname__` attribute, it uses that; otherwise, it uses the method's class name. The function takes no parameters and returns a string.
        
        Returns:
        str: A string representation of the object in the format '<ClassName get_response=MethodName>'.
        """

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
