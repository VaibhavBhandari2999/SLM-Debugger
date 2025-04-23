from importlib import import_module

from django.utils.version import get_docs_version


def deconstructible(*args, path=None):
    """
    Class decorator that allows the decorated class to be serialized
    by the migrations subsystem.

    The `path` kwarg specifies the import path.
    """
    def decorator(klass):
        """
        This function serves as a decorator for a class, enhancing its functionality by adding a custom `__new__` method and a `deconstruct` method. The `__new__` method captures the arguments passed to the class constructor and stores them for later use. The `deconstruct` method returns a 3-tuple containing the class import path, positional arguments, and keyword arguments.
        
        Key Parameters:
        - `klass`: The class to be decorated.
        
        Output:
        - A decorated class with enhanced `
        """

        def __new__(cls, *args, **kwargs):
            """
            This method is a custom `__new__` method for a class. It is responsible for creating a new instance of the class. The method captures the arguments passed during the instantiation process and stores them in the `_constructor_args` attribute of the newly created object. This allows the object to later retrieve the original arguments used to create it.
            
            Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
            Returns:
            An instance of the class with the captured constructor arguments
            """

            # We capture the arguments to make returning them trivial
            obj = super(klass, cls).__new__(cls)
            obj._constructor_args = (args, kwargs)
            return obj

        def deconstruct(obj):
            """
            Return a 3-tuple of class import path, positional arguments,
            and keyword arguments.
            """
            # Fallback version
            if path:
                module_name, _, name = path.rpartition('.')
            else:
                module_name = obj.__module__
                name = obj.__class__.__name__
            # Make sure it's actually there and not an inner class
            module = import_module(module_name)
            if not hasattr(module, name):
                raise ValueError(
                    "Could not find object %s in %s.\n"
                    "Please note that you cannot serialize things like inner "
                    "classes. Please move the object into the main module "
                    "body to use migrations.\n"
                    "For more information, see "
                    "https://docs.djangoproject.com/en/%s/topics/migrations/#serializing-values"
                    % (name, module_name, get_docs_version()))
            return (
                path or '%s.%s' % (obj.__class__.__module__, name),
                obj._constructor_args[0],
                obj._constructor_args[1],
            )

        klass.__new__ = staticmethod(__new__)
        klass.deconstruct = deconstruct

        return klass

    if not args:
        return decorator
    return decorator(*args)
