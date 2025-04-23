import numpy as np

from ..core import indexing
from ..core.utils import Frozen, FrozenDict
from ..core.variable import Variable
from .common import AbstractDataStore, BackendArray
from .file_manager import CachingFileManager
from .locks import HDF5_LOCK, NETCDFC_LOCK, SerializableLock, combine_locks, ensure_lock

# PyNIO can invoke netCDF libraries internally
# Add a dedicated lock just in case NCL as well isn't thread-safe.
NCL_LOCK = SerializableLock()
PYNIO_LOCK = combine_locks([HDF5_LOCK, NETCDFC_LOCK, NCL_LOCK])


class NioArrayWrapper(BackendArray):
    def __init__(self, variable_name, datastore):
        self.datastore = datastore
        self.variable_name = variable_name
        array = self.get_array()
        self.shape = array.shape
        self.dtype = np.dtype(array.typecode())

    def get_array(self, needs_lock=True):
        ds = self.datastore._manager.acquire(needs_lock)
        return ds.variables[self.variable_name]

    def __getitem__(self, key):
        """
        __getitem__(self, key)
        
        Retrieve an element or a slice from the object based on the provided key.
        
        Parameters:
        key (int, slice, or tuple): The index or slice used to retrieve the element or slice from the object.
        
        Returns:
        The element or slice of the object corresponding to the provided key.
        
        This method supports basic indexing and is adapted for explicit indexing using the `indexing.explicit_indexing_adapter` function.
        """

        return indexing.explicit_indexing_adapter(
            key, self.shape, indexing.IndexingSupport.BASIC, self._getitem
        )

    def _getitem(self, key):
        """
        Retrieve an item from the array.
        
        Parameters:
        key (tuple or scalar): The index or key to retrieve from the array.
        
        Returns:
        The value at the specified key in the array.
        
        This method is thread-safe due to the use of a lock. It first acquires the lock,
        then retrieves the array without needing a lock (since it's already held). If the
        key is an empty tuple and the array is zero-dimensional, it returns the scalar
        value directly. Otherwise, it
        """

        with self.datastore.lock:
            array = self.get_array(needs_lock=False)

            if key == () and self.ndim == 0:
                return array.get_value()

            return array[key]


class NioDataStore(AbstractDataStore):
    """Store for accessing datasets via PyNIO
    """

    def __init__(self, filename, mode="r", lock=None, **kwargs):
        import Nio

        if lock is None:
            lock = PYNIO_LOCK
        self.lock = ensure_lock(lock)
        self._manager = CachingFileManager(
            Nio.open_file, filename, lock=lock, mode=mode, kwargs=kwargs
        )
        # xarray provides its own support for FillValue,
        # so turn off PyNIO's support for the same.
        self.ds.set_option("MaskedArrayMode", "MaskedNever")

    @property
    def ds(self):
        return self._manager.acquire()

    def open_store_variable(self, name, var):
        data = indexing.LazilyOuterIndexedArray(NioArrayWrapper(name, self))
        return Variable(var.dimensions, data, var.attributes)

    def get_variables(self):
        """
        Retrieve the variables from the dataset as a FrozenDict.
        
        This method extracts all variables from the dataset and wraps them in a FrozenDict. Each variable is retrieved using the `open_store_variable` method.
        
        Parameters:
        None
        
        Returns:
        FrozenDict: A read-only dictionary containing all variables from the dataset.
        """

        return FrozenDict(
            (k, self.open_store_variable(k, v)) for k, v in self.ds.variables.items()
        )

    def get_attrs(self):
        return Frozen(self.ds.attributes)

    def get_dimensions(self):
        return Frozen(self.ds.dimensions)

    def get_encoding(self):
        return {
            "unlimited_dims": {k for k in self.ds.dimensions if self.ds.unlimited(k)}
        }

    def close(self):
        self._manager.close()
