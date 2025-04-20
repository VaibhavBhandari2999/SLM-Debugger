from io import BytesIO

import numpy as np

from ..core.indexing import NumpyIndexingAdapter
from ..core.utils import Frozen, FrozenDict
from ..core.variable import Variable
from .common import BackendArray, WritableCFDataStore
from .file_manager import CachingFileManager, DummyFileManager
from .locks import ensure_lock, get_write_lock
from .netcdf3 import encode_nc3_attr_value, encode_nc3_variable, is_valid_nc3_name


def _decode_string(s):
    if isinstance(s, bytes):
        return s.decode("utf-8", "replace")
    return s


def _decode_attrs(d):
    # don't decode _FillValue from bytes -> unicode, because we want to ensure
    # that its type matches the data exactly
    return {k: v if k == "_FillValue" else _decode_string(v) for (k, v) in d.items()}


class ScipyArrayWrapper(BackendArray):
    def __init__(self, variable_name, datastore):
        self.datastore = datastore
        self.variable_name = variable_name
        array = self.get_variable().data
        self.shape = array.shape
        self.dtype = np.dtype(array.dtype.kind + str(array.dtype.itemsize))

    def get_variable(self, needs_lock=True):
        ds = self.datastore._manager.acquire(needs_lock)
        return ds.variables[self.variable_name]

    def __getitem__(self, key):
        """
        Retrieve a slice of the data stored in the variable.
        
        This method allows for indexing into the variable's data, returning a
        slice of the data. If the underlying data is memory-mapped, the data
        is copied to ensure safe access even after the file is closed.
        
        Parameters:
        key (int, slice, or array-like): The index or slice to apply to the
        variable's data.
        
        Returns:
        numpy.ndarray: A numpy array containing the sliced data. If the
        """

        data = NumpyIndexingAdapter(self.get_variable().data)[key]
        # Copy data if the source file is mmapped. This makes things consistent
        # with the netCDF4 library by ensuring we can safely read arrays even
        # after closing associated files.
        copy = self.datastore.ds.use_mmap
        return np.array(data, dtype=self.dtype, copy=copy)

    def __setitem__(self, key, value):
        with self.datastore.lock:
            data = self.get_variable(needs_lock=False)
            try:
                data[key] = value
            except TypeError:
                if key is Ellipsis:
                    # workaround for GH: scipy/scipy#6880
                    data[:] = value
                else:
                    raise


def _open_scipy_netcdf(filename, mode, mmap, version):
    """
    Open a NetCDF file using SciPy's netcdf_file.
    
    This function attempts to open a NetCDF file using SciPy's `netcdf_file` interface.
    If the filename ends with '.gz', it will first be decompressed using gzip before
    opening as a NetCDF file. If the filename is a bytestring starting with 'CDF', it
    is treated as a NetCDF3 bytestring. If the file is not a valid NetCDF3 file, a
    `TypeError
    """

    import scipy.io
    import gzip

    # if the string ends with .gz, then gunzip and open as netcdf file
    if isinstance(filename, str) and filename.endswith(".gz"):
        try:
            return scipy.io.netcdf_file(
                gzip.open(filename), mode=mode, mmap=mmap, version=version
            )
        except TypeError as e:
            # TODO: gzipped loading only works with NetCDF3 files.
            if "is not a valid NetCDF 3 file" in e.message:
                raise ValueError(
                    "gzipped file loading only supports " "NetCDF 3 files."
                )
            else:
                raise

    if isinstance(filename, bytes) and filename.startswith(b"CDF"):
        # it's a NetCDF3 bytestring
        filename = BytesIO(filename)

    try:
        return scipy.io.netcdf_file(filename, mode=mode, mmap=mmap, version=version)
    except TypeError as e:  # netcdf3 message is obscure in this case
        errmsg = e.args[0]
        if "is not a valid NetCDF 3 file" in errmsg:
            msg = """
            If this is a NetCDF4 file, you may need to install the
            netcdf4 library, e.g.,

            $ pip install netcdf4
            """
            errmsg += msg
            raise TypeError(errmsg)
        else:
            raise


class ScipyDataStore(WritableCFDataStore):
    """Store for reading and writing data via scipy.io.netcdf.

    This store has the advantage of being able to be initialized with a
    StringIO object, allow for serialization without writing to disk.

    It only supports the NetCDF3 file-format.
    """

    def __init__(
        self, filename_or_obj, mode="r", format=None, group=None, mmap=None, lock=None
    ):
        if group is not None:
            raise ValueError(
                "cannot save to a group with the " "scipy.io.netcdf backend"
            )

        if format is None or format == "NETCDF3_64BIT":
            version = 2
        elif format == "NETCDF3_CLASSIC":
            version = 1
        else:
            raise ValueError("invalid format for scipy.io.netcdf backend: %r" % format)

        if lock is None and mode != "r" and isinstance(filename_or_obj, str):
            lock = get_write_lock(filename_or_obj)

        self.lock = ensure_lock(lock)

        if isinstance(filename_or_obj, str):
            manager = CachingFileManager(
                _open_scipy_netcdf,
                filename_or_obj,
                mode=mode,
                lock=lock,
                kwargs=dict(mmap=mmap, version=version),
            )
        else:
            scipy_dataset = _open_scipy_netcdf(
                filename_or_obj, mode=mode, mmap=mmap, version=version
            )
            manager = DummyFileManager(scipy_dataset)

        self._manager = manager

    @property
    def ds(self):
        return self._manager.acquire()

    def open_store_variable(self, name, var):
        return Variable(
            var.dimensions,
            ScipyArrayWrapper(name, self),
            _decode_attrs(var._attributes),
        )

    def get_variables(self):
        return FrozenDict(
            (k, self.open_store_variable(k, v)) for k, v in self.ds.variables.items()
        )

    def get_attrs(self):
        return Frozen(_decode_attrs(self.ds._attributes))

    def get_dimensions(self):
        return Frozen(self.ds.dimensions)

    def get_encoding(self):
        """
        Retrieve the encoding of the dataset.
        
        This function returns a dictionary containing the encoding information of the dataset. Specifically, it identifies and returns the set of dimension keys that have unlimited dimensions (i.e., dimensions with no specified size).
        
        Returns:
        dict: A dictionary with a single key "unlimited_dims" mapping to a set of dimension keys that have unlimited dimensions.
        
        Example:
        >>> ds = Dataset(...)
        >>> encoding = ds.get_encoding()
        >>> print(encoding)
        {'unlimited_dims':
        """

        encoding = {}
        encoding["unlimited_dims"] = {
            k for k, v in self.ds.dimensions.items() if v is None
        }
        return encoding

    def set_dimension(self, name, length, is_unlimited=False):
        if name in self.ds.dimensions:
            raise ValueError(
                "%s does not support modifying dimensions" % type(self).__name__
            )
        dim_length = length if not is_unlimited else None
        self.ds.createDimension(name, dim_length)

    def _validate_attr_key(self, key):
        if not is_valid_nc3_name(key):
            raise ValueError("Not a valid attribute name")

    def set_attribute(self, key, value):
        """
        Sets an attribute in the NetCDF dataset.
        
        Parameters:
        key (str): The name of the attribute to set.
        value (Any): The value to assign to the attribute. This value will be encoded to a NetCDF-compatible format.
        
        Returns:
        None: This method does not return any value. It modifies the dataset in place.
        
        Notes:
        - The attribute key is first validated using the `_validate_attr_key` method.
        - The value is encoded to a format compatible with Net
        """

        self._validate_attr_key(key)
        value = encode_nc3_attr_value(value)
        setattr(self.ds, key, value)

    def encode_variable(self, variable):
        variable = encode_nc3_variable(variable)
        return variable

    def prepare_variable(
        """
        Prepare a variable for writing to a NetCDF file using the SciPy backend.
        
        This function prepares a variable for writing to a NetCDF file. It creates a variable in the dataset if it does not already exist, sets its attributes, and wraps it in a `ScipyArrayWrapper` for further processing.
        
        Parameters:
        name (str): The name of the variable to be prepared.
        variable (Variable): The variable object containing the data and metadata to be written.
        check_encoding (bool
        """

        self, name, variable, check_encoding=False, unlimited_dims=None
    ):
        if check_encoding and variable.encoding:
            if variable.encoding != {"_FillValue": None}:
                raise ValueError(
                    "unexpected encoding for scipy backend: %r"
                    % list(variable.encoding)
                )

        data = variable.data
        # nb. this still creates a numpy array in all memory, even though we
        # don't write the data yet; scipy.io.netcdf does not not support
        # incremental writes.
        if name not in self.ds.variables:
            self.ds.createVariable(name, data.dtype, variable.dims)
        scipy_var = self.ds.variables[name]
        for k, v in variable.attrs.items():
            self._validate_attr_key(k)
            setattr(scipy_var, k, v)

        target = ScipyArrayWrapper(name, self)

        return target, data

    def sync(self):
        self.ds.sync()

    def close(self):
        self._manager.close()
r.close()
