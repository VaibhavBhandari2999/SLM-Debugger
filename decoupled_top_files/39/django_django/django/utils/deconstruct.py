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
        Return a 3-tuple of class import path, positional arguments,
        and keyword arguments.
        """

        def __new__(cls, *args, **kwargs):
            """
            Create a new instance of the class.
            
            Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
            Returns:
            An instance of the class.
            
            This method is responsible for creating a new instance of the class by capturing the arguments passed during instantiation. It uses the `super()` function to call the parent class's `__new__` method and then stores the captured arguments in the `_constructor_args` attribute of the newly created object.
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
