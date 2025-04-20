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
        Creates a new instance of the class by converting an input object to a NumPy array and then viewing it as an instance of the given class.
        
        Parameters:
        cls (type): The class to which the input object will be viewed.
        obj (array-like): The input object to be converted to a NumPy array.
        *args: Additional arguments to be passed to the NumPy array constructor.
        **kwargs: Additional keyword arguments to be passed to the NumPy array constructor.
        
        Returns:
        """

        self = np.array(obj, *args, **kwargs).view(cls)
        if "info" in getattr(obj, "__dict__", ()):
            self.info = obj.info
        return self

    def __array_finalize__(self, obj):
        """
        Finalize the Column object after it has been initialized from another object.
        
        This method is called after the Column object has been created from another object. It checks if the object is None and returns immediately if so. If the object is not None, it calls the superclass's `__array_finalize__` method if it is callable. After that, it checks if the new Column object was created from a template (e.g., a slice or a scalar multiplication) or through a viewcast (e.g
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
        Generate a pickled representation of the object.
        
        This method is used to create a pickled representation of the object, which is necessary for serialization. It is particularly useful for subclasses of `NdArrayMixin`, which are subclasses of `ndarray`.
        
        Parameters:
        None
        
        Returns:
        tuple: A tuple containing the pickled state of the object. The tuple includes the pickled state of the superclass, followed by the object's dictionary state.
        
        Notes:
        This method is a custom implementation of the
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
