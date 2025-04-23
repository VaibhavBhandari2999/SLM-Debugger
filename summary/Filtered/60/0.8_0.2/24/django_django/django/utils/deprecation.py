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
        class_name (str): The name of the class that contains the deprecated method.
        old_method_name (str): The name of the deprecated method.
        new_method_name (str): The name of the new method that should be used instead.
        deprecation_warning (str): The warning message to be displayed when the deprecated method is used.
        
        Returns:
        None: This function does not return any value.
        """

        self.class_name = class_name
        self.old_method_name = old_method_name
        self.new_method_name = new_method_name
        self.deprecation_warning = deprecation_warning

    def __call__(self, f):
        """
        A decorator that deprecates a method in a class.
        
        This function wraps a method in a class, issuing a deprecation warning each time the method is called. The warning message indicates that the method is deprecated and suggests an alternative.
        
        Parameters:
        f (function): The method to be deprecated.
        
        Returns:
        function: A wrapped function that issues a deprecation warning and calls the original method.
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
        """
        Method: __instancecheck__
        
        This method is a deprecated version of the instance check for a custom type or class. It is intended to be overridden in a subclass to define custom instance checking logic. The method first issues a warning to users about its deprecation and suggests an alternative method to use. It then delegates the actual instance check to the superclass's `__instancecheck__` method.
        
        Parameters:
        - instance (object): The object to check if it is an instance of the class or a
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
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response
n response
