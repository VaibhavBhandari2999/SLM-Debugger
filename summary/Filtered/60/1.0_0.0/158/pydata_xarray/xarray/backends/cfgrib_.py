import numpy as np

from ..core import indexing
from ..core.utils import Frozen, FrozenDict
from ..core.variable import Variable
from .common import AbstractDataStore, BackendArray
from .locks import SerializableLock, ensure_lock

# FIXME: Add a dedicated lock, even if ecCodes is supposed to be thread-safe
#   in most circumstances. See:
#       https://confluence.ecmwf.int/display/ECC/Frequently+Asked+Questions
ECCODES_LOCK = SerializableLock()


class CfGribArrayWrapper(BackendArray):
    def __init__(self, datastore, array):
        self.datastore = datastore
        self.shape = array.shape
        self.dtype = array.dtype
        self.array = array

    def __getitem__(self, key):
        return indexing.explicit_indexing_adapter(
            key, self.shape, indexing.IndexingSupport.OUTER, self._getitem
        )

    def _getitem(self, key):
        with self.datastore.lock:
            return self.array[key]


class CfGribDataStore(AbstractDataStore):
    """
    Implements the ``xr.AbstractDataStore`` read-only API for a GRIB file.
    """

    def __init__(self, filename, lock=None, **backend_kwargs):
        import cfgrib

        if lock is None:
            lock = ECCODES_LOCK
        self.lock = ensure_lock(lock)
        self.ds = cfgrib.open_file(filename, **backend_kwargs)

    def open_store_variable(self, name, var):
        """
        Open a store variable from a CF-Grib dataset.
        
        This function takes a variable from a CF-Grib dataset and wraps it in a `Variable` object, ensuring that the data is properly handled and encoded. The function supports both numpy arrays and custom `CfGribArrayWrapper` objects.
        
        Parameters:
        name (str): The name of the variable.
        var (Variable): The variable object from the CF-Grib dataset.
        
        Returns:
        Variable: A `Variable` object with the
        """

        if isinstance(var.data, np.ndarray):
            data = var.data
        else:
            wrapped_array = CfGribArrayWrapper(self, var.data)
            data = indexing.LazilyOuterIndexedArray(wrapped_array)

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
        
        This function returns the encoding of the dataset, specifically identifying any dimensions that are unlimited.
        
        Returns:
        dict: A dictionary containing a single key-value pair. The key is 'unlimited_dims' and the value is a set of dimension names that do not have a specified size (i.e., their size is None).
        
        Example:
        >>> obj = DatasetObject()
        >>> obj.get_dimensions()  # Assume this returns a dictionary with some dimensions having None as their
        """

        dims = self.get_dimensions()
        encoding = {"unlimited_dims": {k for k, v in dims.items() if v is None}}
        return encoding
