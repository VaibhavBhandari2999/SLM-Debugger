# Licensed under a 3-clause BSD style license - see LICENSE.rst
from ...utils.misc import InheritDocstrings


class _FormatterMeta(InheritDocstrings):
    registry = {}

    def __new__(mcls, name, bases, members):
        """
        This method is a class method that is called during the creation of a new instance of a class. It is responsible for setting up the class and registering it with a registry based on a name derived from the class or a specified member.
        
        Parameters:
        - mcls: The metaclass of the class being created.
        - name: The name of the class being created.
        - bases: A tuple of base classes for the new class.
        - members: A dictionary containing the members (attributes and methods) of
        """

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
        This function is a custom `__new__` method for a class that prevents instantiation. It returns the class itself rather than an instance. No parameters or keyword arguments are accepted. The function does not return any value other than the class itself.
        
        Parameters:
        - cls: The class itself, which is the Formatter class in this context.
        
        Returns:
        - cls: The class itself, indicating that the class cannot be instantiated and attempting to do so will simply return the class.
        
        Note:
        - This method is
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
