class Bunch(dict):
    """Container object exposing keys as attributes.

    Bunch objects are sometimes used as an output for functions and methods.
    They extend dictionaries by enabling values to be accessed by key,
    `bunch["value_key"]`, or by an attribute, `bunch.value_key`.

    Examples
    --------
    >>> from sklearn.utils import Bunch
    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6
    """

    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()

    def __getattr__(self, key):
        """
        __getattr__(self, key)
        
        This method is a special method in Python that is called when an attribute lookup has not found the attribute in the usual places. It is particularly useful for implementing dynamic attribute access.
        
        Parameters:
        key (str): The name of the attribute being accessed.
        
        Returns:
        The value of the attribute if it exists, otherwise raises an AttributeError with the name of the missing attribute.
        
        This method allows for custom behavior when an attribute is accessed that does not exist in the usual
        """

        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        """
        Set the state of the object.
        
        This method is used to unpickle the object and restore its state. In the original implementation, it was designed to handle pickles generated with scikit-learn 0.16.*, where the non-empty `__dict__` of Bunch objects could cause unexpected behavior when loading pickles with scikit-learn 0.17. To avoid this issue, the method is overridden to do nothing, effectively ignoring the pickled `__dict__`.
        """

        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass
