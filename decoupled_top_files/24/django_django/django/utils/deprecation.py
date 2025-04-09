import inspect
import warnings


class RemovedInNextVersionWarning(DeprecationWarning):
    pass


class RemovedInDjango40Warning(PendingDeprecationWarning):
    pass


class warn_about_renamed_method:
    def __init__(self, class_name, old_method_name, new_method_name, deprecation_warning):
        """
        This function initializes an instance of the DeprecationWarning class with the provided parameters.
        
        Args:
        class_name (str): The name of the class that the deprecated method belongs to.
        old_method_name (str): The name of the deprecated method.
        new_method_name (str): The name of the new method that should be used instead.
        deprecation_warning (str): A warning message to be displayed when the deprecated method is called.
        
        Returns:
        None: This function does
        """

        self.class_name = class_name
        self.old_method_name = old_method_name
        self.new_method_name = new_method_name
        self.deprecation_warning = deprecation_warning

    def __call__(self, f):
        """
        Summary line: Warns users that the method they are using is deprecated and should be replaced with a new one.
        
        Extended description of function.
        
        Args:
        f (function): The function being decorated.
        
        Returns:
        function: A wrapped function that issues a deprecation warning before calling the original function.
        
        Example:
        >>> @deprecated(old_method_name='old_func', new_method_name='new_func')
        ... def old_func(x):
        ...     return x * 2
        """

        def wrapped(*args, **kwargs):
            """
            Summary: Warns about deprecation of a method and calls the original function.
            
            Args:
            *args: Variable length argument list passed to the original function.
            **kwargs: Arbitrary keyword arguments passed to the original function.
            
            Returns:
            The result of calling the original function `f` with the provided arguments.
            
            Raises:
            self.deprecation_warning: A warning indicating that the method is deprecated and suggesting an alternative.
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
        This function is a metaclass method that dynamically modifies the class attributes during the class creation process. It iterates through the methods of the base classes and renames them according to the specified rules. If a method is renamed, a deprecation warning is issued. The function also ensures that both the old and new method names are present in the class.
        
        Args:
        cls: The class being created.
        name: The name of the class being created.
        bases: A tuple of base classes
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
        Checks if an instance is an instance of the class.
        
        This method issues a deprecation warning and then checks if the given instance is an instance of the class using the `__instancecheck__` method of the superclass.
        
        Args:
        instance: The instance to check.
        
        Returns:
        bool: True if the instance is an instance of the class, False otherwise.
        
        Raises:
        DeprecationWarning: If the method is called, indicating that the usage is deprecated.
        """

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
        Calls the process_request method if it exists, then calls get_response with the request if no response is returned from process_request. If process_response method exists, it is called with the request and response. Returns the final response.
        """

        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response
