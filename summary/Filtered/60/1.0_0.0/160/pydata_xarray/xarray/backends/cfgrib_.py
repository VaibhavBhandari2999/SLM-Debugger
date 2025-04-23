import os
import warnings

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
from .locks import SerializableLock, ensure_lock
from .store import StoreBackendEntrypoint

try:
    import cfgrib

    has_cfgrib = True
except ModuleNotFoundError:
    has_cfgrib = False
# cfgrib throws a RuntimeError if eccodes is not installed
except RuntimeError:
    warnings.warn(
        "Failed to load cfgrib - most likely eccodes is missing. Try `import cfgrib` to get the error message"
    )
    has_cfgrib = False

# FIXME: Add a dedicated lock, even if ecCodes is supposed to be thread-safe
#   in most circumstances. See:
#       https://confluence.ecmwf.int/display/ECC/Frequently+Asked+Questions
ECCODES_LOCK = SerializableLock()


class CfGribArrayWrapper(BackendArray):
    def __init__(self, datastore, array):
        """
        Initialize a custom array-like object.
        
        Args:
        datastore (object): The underlying data storage object.
        array (numpy.ndarray): The array data to be stored.
        
        Attributes:
        datastore (object): The underlying data storage object.
        shape (tuple): The shape of the array.
        dtype (numpy.dtype): The data type of the array elements.
        array (numpy.ndarray): The stored array data.
        """

        self.datastore = datastore
        self.shape = array.shape
        self.dtype = array.dtype
        self.array = array

    def __getitem__(self, key):
        return indexing.explicit_indexing_adapter(
            key, self.shape, indexing.IndexingSupport.BASIC, self._getitem
        )

    def _getitem(self, key):
        with self.datastore.lock:
            return self.array[key]


class CfGribDataStore(AbstractDataStore):
    """
    Implements the ``xr.AbstractDataStore`` read-only API for a GRIB file.
    """

    def __init__(self, filename, lock=None, **backend_kwargs):

        if lock is None:
            lock = ECCODES_LOCK
        self.lock = ensure_lock(lock)
        self.ds = cfgrib.open_file(filename, **backend_kwargs)

    def open_store_variable(self, name, var):
        if isinstance(var.data, np.ndarray):
            data = var.data
        else:
            wrapped_array = CfGribArrayWrapper(self, var.data)
            data = indexing.LazilyIndexedArray(wrapped_array)

        encoding = self.ds.encoding.copy()
        encoding["original_shape"] = var.data.shape

        return Variable(var.dimensions, data, var.attributes, encoding)

    def get_variables(self):
        return FrozenDict(
            (k, self.open_store_variable(k, v)) for k, v in self.ds.variables.items()
        )

    def get_attrs(self):
        return Frozen(self.ds.attributes)

    def get_dimensions(self):
        return Frozen(self.ds.dimensions)

    def get_encoding(self):
        """
        Retrieve the encoding of the dataset.
        
        This function returns a dictionary representing the encoding of the dataset. The dictionary includes a key 'unlimited_dims' that contains a set of dimension names that do not have a specified size (i.e., their size is `None`).
        
        Parameters:
        None
        
        Returns:
        dict: A dictionary with a single key 'unlimited_dims' whose value is a set of dimension names with unspecified sizes.
        """

        dims = self.get_dimensions()
        encoding = {"unlimited_dims": {k for k, v in dims.items() if v is None}}
        return encoding


class CfgribfBackendEntrypoint(BackendEntrypoint):
    def guess_can_open(self, filename_or_obj):
        try:
            _, ext = os.path.splitext(filename_or_obj)
        except TypeError:
            return False
        return ext in {".grib", ".grib2", ".grb", ".grb2"}

    def open_dataset(
        self,
        filename_or_obj,
        *,
        mask_and_scale=True,
        decode_times=True,
        concat_characters=True,
        decode_coords=True,
        drop_variables=None,
        use_cftime=None,
        decode_timedelta=None,
        lock=None,
        indexpath="{path}.{short_hash}.idx",
        filter_by_keys={},
        read_keys=[],
        encode_cf=("parameter", "time", "geography", "vertical"),
        squeeze=True,
        time_dims=("time", "step"),
    ):

        store = CfGribDataStore(
            filename_or_obj,
            indexpath=indexpath,
            filter_by_keys=filter_by_keys,
            read_keys=read_keys,
            encode_cf=encode_cf,
            squeeze=squeeze,
            time_dims=time_dims,
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


if has_cfgrib:
    BACKEND_ENTRYPOINTS["cfgrib"] = CfgribfBackendEntrypoint
n_error(store):
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


if has_cfgrib:
    BACKEND_ENTRYPOINTS["cfgrib"] = CfgribfBackendEntrypoint
