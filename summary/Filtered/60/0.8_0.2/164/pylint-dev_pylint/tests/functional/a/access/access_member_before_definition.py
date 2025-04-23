# pylint: disable=missing-docstring,too-few-public-methods,invalid-name
# pylint: disable=attribute-defined-outside-init, useless-object-inheritance


class Aaaa(object):
    """class with attributes defined in wrong order"""

    def __init__(self):
        """
        Initialize the object with predefined values.
        
        This method sets up the object by initializing its attributes.
        
        Parameters:
        None
        
        Attributes:
        _var2 (int): An integer value set to 3.
        _var3 (int): An integer value initialized with the value of _var2.
        
        Returns:
        None
        """

        var1 = self._var2  # [access-member-before-definition]
        self._var2 = 3
        self._var3 = var1


class Bbbb(object):
    A = 23
    B = A

    def __getattr__(self, attr):
        """
        Method: __getattr__
        Summary: This method is a special method in Python that is called when an attribute lookup fails for an object. It is used to handle attribute access that does not exist in the object's namespace.
        Parameters:
        - attr (str): The attribute that was not found in the object's namespace.
        Returns:
        - The value of the attribute if it is successfully set, otherwise the attribute itself is returned.
        Raises:
        - AttributeError
        """

        try:
            return self.__repo
        except AttributeError:
            self.__repo = attr
            return attr

    def catchme(self, attr):
        """no AttributeError caught"""
        try:
            return self._repo  # [access-member-before-definition]
        except ValueError:
            self._repo = attr
            return attr


class Mixin(object):
    def test_mixin(self):
        """Don't emit access-member-before-definition for mixin classes."""
        if self.already_defined:
            # pylint: disable=attribute-defined-outside-init
            self.already_defined = None


# Test for regression in bitbucket issue 164
# https://bitbucket.org/logilab/pylint/issue/164/
class MyClass1:
    def __init__(self):
        self.first += 5  # [access-member-before-definition]
        self.first = 0
