from sympy.utilities.exceptions import SymPyDeprecationWarning
from sympy.core.core import BasicMeta, Registry, all_classes


class ClassRegistry(Registry):
    """
    Namespace for SymPy classes

    This is needed to avoid problems with cyclic imports.
    To get a SymPy class, use `C.<class_name>` e.g. `C.Rational`, `C.Add`.

    For performance reasons, this is coupled with a set `all_classes` holding
    the classes, which should not be modified directly.
    """
    __slots__ = ()

    def __setattr__(self, name, cls):
        Registry.__setattr__(self, name, cls)
        all_classes.add(cls)

    def __delattr__(self, name):
        """
        Delete an attribute from the object.
        
        Parameters:
        name (str): The name of the attribute to delete.
        
        This method first retrieves the class associated with the given attribute name. It then deletes the attribute from the object itself and from the Registry. Additionally, it ensures that the class is not present in the `all_classes` list before removing it from there. If the class is no longer found in the object's class dictionary, it is removed from `all_classes`.
        
        Note:
        This method is
        """

        cls = getattr(self, name)
        Registry.__delattr__(self, name)
        # The same class could have different names, so make sure
        # it's really gone from C before removing it from all_classes.
        if cls not in self.__class__.__dict__.itervalues():
            all_classes.remove(cls)

    def __getattr__(self, name):
        """
        Get a class by name.
        
        This method is deprecated and should not be used. Instead, use direct imports from the defining module.
        
        Parameters
        ----------
        name : str
        The name of the class to retrieve.
        
        Returns
        -------
        cls : class
        The class corresponding to the given name.
        
        Notes
        -----
        This method is deprecated as of SymPy 1.0 and will be removed in a future version. Use direct imports from the defining module instead.
        
        Examples
        --------
        >>> from sympy import Class
        """

        # Warning on hasattr(C, '__wrapped__') leadds to warnings during test
        # collection when running doctests under pytest.
        if name != '__wrapped__':
            SymPyDeprecationWarning(
                feature='C, including its class ClassRegistry,',
                last_supported_version='1.0',
                useinstead='direct imports from the defining module',
                issue=9371,
                deprecated_since_version='1.0').warn(stacklevel=2)

        return any(cls.__name__ == name for cls in all_classes)

    @property
    def _sympy_(self):
        # until C is deprecated, any sympification of an expression
        # with C when C has not been defined can raise this error
        # since the user is trying to use C like a symbol -- and if
        # we get here, it hasn't been defined as a symbol
        raise NameError("name 'C' is not defined as a Symbol")

C = ClassRegistry()
C.BasicMeta = BasicMeta
