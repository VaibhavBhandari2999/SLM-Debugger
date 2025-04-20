# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np

from astropy.utils.data_info import ParentDtypeInfo


class NdarrayMixinInfo(ParentDtypeInfo):
    _represent_as_dict_primary_data = "data"

    def _represent_as_dict(self):
        """Represent Column as a dict that can be serialized."""
        col = self._parent
        out = {"data": col.view(np.ndarray)}
        return out

    def _construct_from_dict(self, map):
        """Construct Column from ``map``."""
        data = map.pop("data")
        out = self._parent_cls(data, **map)
        return out


class NdarrayMixin(np.ndarray):
    """
    Mixin column class to allow storage of arbitrary numpy
    ndarrays within a Table.  This is a subclass of numpy.ndarray
    and has the same initialization options as ``np.array()``.
    """

    info = NdarrayMixinInfo()

    def __new__(cls, obj, *args, **kwargs):
        """
        Constructs a new instance of a NumPy array view with the specified class (cls) and initializes it with the given object (obj). The new array can optionally accept additional arguments (*args) and keyword arguments (**kwargs) for the array initialization. If the input object (obj) has an attribute 'info' in its dictionary, this attribute is copied to the new array's 'info' attribute.
        
        Parameters:
        cls (class): The class to which the new array will be viewed.
        """

        self = np.array(obj, *args, **kwargs).view(cls)
        if "info" in getattr(obj, "__dict__", ()):
            self.info = obj.info
        return self

    def __array_finalize__(self, obj):
        """
        Finalizes the array creation process for the Column object.
        
        This method is called after the array has been created and is used to initialize the Column attributes from the provided object. If the object is None, this method does nothing. If the object is callable, it is called with the object as an argument.
        
        Parameters:
        obj (object): The object from which to initialize the Column attributes.
        
        Returns:
        None: This method does not return anything. It modifies the current instance in place.
        
        Notes:
        """

        if obj is None:
            return

        if callable(super().__array_finalize__):
            super().__array_finalize__(obj)

        # Self was created from template (e.g. obj[slice] or (obj * 2))
        # or viewcast e.g. obj.view(Column).  In either case we want to
        # init Column attributes for self from obj if possible.
        if "info" in getattr(obj, "__dict__", ()):
            self.info = obj.info

    def __reduce__(self):
        """
        This function is used to customize the pickling process for objects derived from `NdArrayMixin`. It returns a tuple that represents the state of the object during pickling. The function overrides the default `__reduce__` method to include additional state information, specifically the object's dictionary.
        
        Key Parameters:
        - `self`: The instance of the class that is being pickled.
        
        Output:
        - A tuple containing the state of the object suitable for pickling. The tuple includes:
        - The first element
        """

        # patch to pickle NdArrayMixin objects (ndarray subclasses), see
        # http://www.mail-archive.com/numpy-discussion@scipy.org/msg02446.html

        object_state = list(super().__reduce__())
        object_state[2] = (object_state[2], self.__dict__)
        return tuple(object_state)

    def __setstate__(self, state):
        # patch to unpickle NdarrayMixin objects (ndarray subclasses), see
        # http://www.mail-archive.com/numpy-discussion@scipy.org/msg02446.html

        nd_state, own_state = state
        super().__setstate__(nd_state)
        self.__dict__.update(own_state)
