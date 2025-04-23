import numpy as np

from ..core import indexing
from ..core.utils import Frozen, FrozenDict, close_on_error
from ..core.variable import Variable
from .common import (
    BACKEND_ENTRYPOINTS,
    AbstractDataStore,
    BackendArray,
    BackendEntrypoint,
)
from .file_manager import CachingFileManager
from .locks import HDF5_LOCK, NETCDFC_LOCK, SerializableLock, combine_locks, ensure_lock
from .store import StoreBackendEntrypoint

try:
    import Nio

    has_pynio = True
except ModuleNotFoundError:
    has_pynio = False


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
        return indexing.explicit_indexing_adapter(
            key, self.shape, indexing.IndexingSupport.BASIC, self._getitem
        )

    def _getitem(self, key):
        """
        Retrieve an element from the array.
        
        Parameters:
        key (tuple): The index key to access the element in the array.
        
        Returns:
        The value at the specified index in the array.
        
        This method is thread-safe due to the use of a lock. It first acquires the lock, then retrieves the array without needing a lock, and finally accesses the element at the given index. If the key is an empty tuple and the array is zero-dimensional, it returns the scalar value directly. Otherwise,
        """

        with self.datastore.lock:
            array = self.get_array(needs_lock=False)

            if key == () and self.ndim == 0:
                return array.get_value()

            return array[key]


class NioDataStore(AbstractDataStore):
    """Store for accessing datasets via PyNIO"""

    def __init__(self, filename, mode="r", lock=None, **kwargs):

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
        data = indexing.LazilyIndexedArray(NioArrayWrapper(name, self))
        return Variable(var.dimensions, data, var.attributes)

    def get_variables(self):
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


class PynioBackendEntrypoint(BackendEntrypoint):
    def open_dataset(
        """
        Open a NetCDF dataset from a file or file-like object.
        
        Parameters:
        filename_or_obj (str or file-like object): The filename or file-like object to open.
        mask_and_scale (bool, optional): If True, apply mask and scaling to variables. Default is True.
        decode_times (bool, optional): If True, decode time coordinate variables. Default is True.
        concat_characters (bool, optional): If True, concatenate character variables. Default is True.
        decode_coords
        """

        self,
        filename_or_obj,
        mask_and_scale=True,
        decode_times=True,
        concat_characters=True,
        decode_coords=True,
        drop_variables=None,
        use_cftime=None,
        decode_timedelta=None,
        mode="r",
        lock=None,
    ):
        store = NioDataStore(
            filename_or_obj,
            mode=mode,
            lock=lock,
        )

        store_entrypoint = StoreBackendEntrypoint()
        with close_on_error(store):
            ds = store_entrypoint.open_dataset(
                store,
                mask_and_scale=mask_and_scale,
                decode_times=decode_times,
                concat_characters=concat_characters,
                decode_coords=decode_coords,
                drop_variables=drop_variables,
                use_cftime=use_cftime,
                decode_timedelta=decode_timedelta,
            )
        return ds


if has_pynio:
    BACKEND_ENTRYPOINTS["pynio"] = PynioBackendEntrypoint
