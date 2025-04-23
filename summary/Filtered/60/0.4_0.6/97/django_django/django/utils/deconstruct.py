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
        Decorator function that modifies a class to support custom serialization and deserialization.
        
        This decorator adds functionality to a class to allow for custom serialization and deserialization of instances. It captures the constructor arguments of the class when an instance is created and provides a method to reconstruct the instance from the serialized data.
        
        Parameters:
        klass (type): The class to be decorated.
        
        Returns:
        type: The decorated class with enhanced serialization and deserialization capabilities.
        
        Methods:
        __new__(cls, *args, **kwargs
        """

        def __new__(cls, *args, **kwargs):
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
            if path and type(obj) is klass:
                module_name, _, name = path.rpartition(".")
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
                    "https://docs.djangoproject.com/en/%s/topics/migrations/"
                    "#serializing-values" % (name, module_name, get_docs_version())
                )
            return (
                path
                if path and type(obj) is klass
                else f"{obj.__class__.__module__}.{name}",
                obj._constructor_args[0],
                obj._constructor_args[1],
            )

        klass.__new__ = staticmethod(__new__)
        klass.deconstruct = deconstruct

        return klass

    if not args:
        return decorator
    return decorator(*args)
