import inspect
import warnings


class RemovedInNextVersionWarning(DeprecationWarning):
    pass


class RemovedInDjango40Warning(PendingDeprecationWarning):
    pass


class warn_about_renamed_method:
    def __init__(self, class_name, old_method_name, new_method_name, deprecation_warning):
        """
        Initialize a DeprecationWarning object.
        
        Args:
        class_name (str): The name of the class from which the deprecated method is being called.
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
        """
        This function is a decorator that wraps another function `f`. It issues a deprecation warning when the wrapped function is called, directing the user to a new method. The warning is generated using the `warnings.warn` function with a custom message that includes the class name, the old method name, and the new method name. The decorator returns the wrapped function `wrapped`, which in turn calls the original function `f` with any provided arguments and keyword arguments.
        
        Parameters:
        - f (function):
        """

        def wrapped(*args, **kwargs):
            """
            This function is a wrapper that deprecates the use of a specific method in favor of a new one. It issues a deprecation warning when the deprecated method is called.
            
            Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
            Returns:
            The result of calling the original function `f` with the provided arguments and keyword arguments.
            
            Warning:
            This function is deprecated. Use the new method specified in the warning message instead.
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
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        """
        Process a request and generate a response.
        
        This method is called to handle a request. It first checks if the instance has a `process_request` method and invokes it if present. If `process_request` returns a response, it is used. Otherwise, it proceeds to generate a response using the `get_response` method. After generating the response, it checks if the instance has a `process_response` method and invokes it, passing the original request and the generated response. The final response is then
        """

        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response
