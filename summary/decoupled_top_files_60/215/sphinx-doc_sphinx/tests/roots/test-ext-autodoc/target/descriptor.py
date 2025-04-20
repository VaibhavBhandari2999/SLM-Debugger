class CustomDataDescriptor(object):
    """Descriptor class docstring."""

    def __init__(self, doc):
        self.__doc__ = doc

    def __get__(self, obj, type=None):
        """
        __get__(self, obj, type=None)
        
        A descriptor method that returns 42 when called with an object and type. If the object is None, it returns the descriptor itself.
        
        Parameters:
        - self: The descriptor instance.
        - obj: The object the descriptor is accessed through (None if accessed via the class itself).
        - type: The class type (optional).
        
        Returns:
        - 42 if obj is not None, otherwise returns the descriptor
        """

        if obj is None:
            return self
        return 42

    def meth(self):
        """Function."""
        return "The Answer"


class CustomDataDescriptorMeta(type):
    """Descriptor metaclass docstring."""


class CustomDataDescriptor2(CustomDataDescriptor):
    """Descriptor class with custom metaclass docstring."""
    __metaclass__ = CustomDataDescriptorMeta


class Class:
    descr = CustomDataDescriptor("Descriptor instance docstring.")

    @property
    def prop(self):
        """Property."""
