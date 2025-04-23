class CustomDataDescriptor(object):
    """Descriptor class docstring."""

    def __init__(self, doc):
        self.__doc__ = doc

    def __get__(self, obj, type=None):
        """
        __get__(self, obj, type=None)
        Get the value of the descriptor.
        
        Parameters:
        - self: The descriptor instance.
        - obj: The object for which the descriptor is being accessed (None if accessed on the class itself).
        - type: The class type (optional).
        
        Returns:
        - The value of the descriptor (42 in this case) if accessed on an instance, or the descriptor instance itself if accessed on the class.
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
