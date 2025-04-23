# Licensed under a 3-clause BSD style license - see LICENSE.rst
from ...utils.misc import InheritDocstrings


class _FormatterMeta(InheritDocstrings):
    registry = {}

    def __new__(mcls, name, bases, members):
        if 'name' in members:
            formatter_name = members['name'].lower()
        else:
            formatter_name = members['name'] = name.lower()

        cls = super().__new__(mcls, name, bases, members)

        mcls.registry[formatter_name] = cls

        return cls


class Base(metaclass=_FormatterMeta):
    """
    The abstract base class of all unit formats.
    """

    def __new__(cls, *args, **kwargs):
        """
        This function is a custom `__new__` method for a class, designed to prevent instantiation of the Formatter class. It does not accept any arguments and does not return an instance of the class. Instead, it returns the class itself. This method is typically used in singleton patterns or when a class should not be instantiated directly.
        
        Parameters:
        - *args: Variable length argument list. Not used in this context.
        - **kwargs: Arbitrary keyword arguments. Not used in this context.
        
        Returns:
        -
        """

        # This __new__ is to make it clear that there is no reason to
        # instantiate a Formatter--if you try to you'll just get back the
        # class
        return cls

    @classmethod
    def parse(cls, s):
        """
        Convert a string to a unit object.
        """

        raise NotImplementedError(
            "Can not parse {0}".format(cls.__name__))

    @classmethod
    def to_string(cls, u):
        """
        Convert a unit object to a string.
        """

        raise NotImplementedError(
            "Can not output in {0} format".format(cls.__name__))
