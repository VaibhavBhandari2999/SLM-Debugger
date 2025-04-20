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
        Create a new instance of the class from the given object.
        
        Parameters:
        obj (array-like): The input object to be converted into a new instance of the class.
        *args: Additional positional arguments to be passed to the `np.array` constructor.
        **kwargs: Additional keyword arguments to be passed to the `np.array` constructor.
        
        Returns:
        cls: A new instance of the class, derived from the input object and with additional attributes if available.
        
        This method is a custom `
        """

        self = np.array(obj, *args, **kwargs).view(cls)
        if "info" in getattr(obj, "__dict__", ()):
            self.info = obj.info
        return self

    def __array_finalize__(self, obj):
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
        Reduces the object to a format that can be pickled. This function is specifically designed to handle `NdArrayMixin` objects, which are subclasses of `ndarray`. The function returns a tuple containing the pickled state of the object, along with its dictionary attributes.
        
        Parameters:
        - None (the function relies on the internal state of the object)
        
        Returns:
        - A tuple containing:
        - The pickled state of the object (result of `super().__reduce__()`).
        - An
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
