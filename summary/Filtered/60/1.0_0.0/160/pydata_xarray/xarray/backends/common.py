import logging
import time
import traceback
from typing import Any, Dict, Tuple, Type, Union

import numpy as np

from ..conventions import cf_encoder
from ..core import indexing
from ..core.pycompat import is_duck_dask_array
from ..core.utils import FrozenDict, NdimSizeLenMixin

# Create a logger object, but don't add any handlers. Leave that to user code.
logger = logging.getLogger(__name__)


NONE_VAR_NAME = "__values__"


def _encode_variable_name(name):
    """
    Encodes a variable name for use in a Python context.
    
    Args:
    name (str, optional): The original variable name to be encoded. If None, it is set to a default value 'NONE_VAR_NAME'. Defaults to None.
    
    Returns:
    str: The encoded variable name suitable for use in Python code.
    
    Raises:
    TypeError: If the provided name is not a string.
    """

    if name is None:
        name = NONE_VAR_NAME
    return name


def _decode_variable_name(name):
    """
    Decodes a variable name from a string representation.
    
    Args:
    name (str): The string representation of the variable name.
    
    Returns:
    The decoded variable name (str or None).
    
    Raises:
    ValueError: If the input is not a string.
    
    Examples:
    >>> _decode_variable_name('my_var')
    'my_var'
    >>> _decode_variable_name(NONE_VAR_NAME)
    None
    """

    if name == NONE_VAR_NAME:
        name = None
    return name


def find_root_and_group(ds):
    """Find the root and group name of a netCDF4/h5netcdf dataset."""
    hierarchy = ()
    while ds.parent is not None:
        hierarchy = (ds.name.split("/")[-1],) + hierarchy
        ds = ds.parent
    group = "/" + "/".join(hierarchy)
    return ds, group


def robust_getitem(array, key, catch=Exception, max_retries=6, initial_delay=500):
    """
    Robustly index an array, using retry logic with exponential backoff if any
    of the errors ``catch`` are raised. The initial_delay is measured in ms.

    With the default settings, the maximum delay will be in the range of 32-64
    seconds.
    """
    assert max_retries >= 0
    for n in range(max_retries + 1):
        try:
            return array[key]
        except catch:
            if n == max_retries:
                raise
            base_delay = initial_delay * 2 ** n
            next_delay = base_delay + np.random.randint(base_delay)
            msg = (
                "getitem failed, waiting %s ms before trying again "
                "(%s tries remaining). Full traceback: %s"
                % (next_delay, max_retries - n, traceback.format_exc())
            )
            logger.debug(msg)
            time.sleep(1e-3 * next_delay)


class BackendArray(NdimSizeLenMixin, indexing.ExplicitlyIndexed):
    __slots__ = ()

    def __array__(self, dtype=None):
        key = indexing.BasicIndexer((slice(None),) * self.ndim)
        return np.asarray(self[key], dtype=dtype)


class AbstractDataStore:
    __slots__ = ()

    def get_dimensions(self):  # pragma: no cover
        raise NotImplementedError()

    def get_attrs(self):  # pragma: no cover
        raise NotImplementedError()

    def get_variables(self):  # pragma: no cover
        raise NotImplementedError()

    def get_encoding(self):
        return {}

    def load(self):
        """
        This loads the variables and attributes simultaneously.
        A centralized loading function makes it easier to create
        data stores that do automatic encoding/decoding.

        For example::

            class SuffixAppendingDataStore(AbstractDataStore):

                def load(self):
                    variables, attributes = AbstractDataStore.load(self)
                    variables = {'%s_suffix' % k: v
                                 for k, v in variables.items()}
                    attributes = {'%s_suffix' % k: v
                                  for k, v in attributes.items()}
                    return variables, attributes

        This function will be called anytime variables or attributes
        are requested, so care should be taken to make sure its fast.
        """
        variables = FrozenDict(
            (_decode_variable_name(k), v) for k, v in self.get_variables().items()
        )
        attributes = FrozenDict(self.get_attrs())
        return variables, attributes

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()


class ArrayWriter:
    __slots__ = ("sources", "targets", "regions", "lock")

    def __init__(self, lock=None):
        self.sources = []
        self.targets = []
        self.regions = []
        self.lock = lock

    def add(self, source, target, region=None):
        if is_duck_dask_array(source):
            self.sources.append(source)
            self.targets.append(target)
            self.regions.append(region)
        else:
            if region:
                target[region] = source
            else:
                target[...] = source

    def sync(self, compute=True):
        """
        Synchronize source data to target data using Dask for parallel processing.
        
        This method synchronizes the data stored in the `sources` attribute to the `targets` attribute using Dask's `da.store` method. The synchronization is performed in parallel if the `compute` parameter is set to `True`.
        
        Parameters:
        compute (bool, optional): If `True`, the synchronization will be executed immediately. If `False`, the synchronization will be scheduled but not executed. Default is `True`.
        
        Returns
        """

        if self.sources:
            import dask.array as da

            # TODO: consider wrapping targets with dask.delayed, if this makes
            # for any discernable difference in perforance, e.g.,
            # targets = [dask.delayed(t) for t in self.targets]

            delayed_store = da.store(
                self.sources,
                self.targets,
                lock=self.lock,
                compute=compute,
                flush=True,
                regions=self.regions,
            )
            self.sources = []
            self.targets = []
            self.regions = []
            return delayed_store


class AbstractWritableDataStore(AbstractDataStore):
    __slots__ = ()

    def encode(self, variables, attributes):
        """
        Encode the variables and attributes in this store

        Parameters
        ----------
        variables : dict-like
            Dictionary of key/value (variable name / xr.Variable) pairs
        attributes : dict-like
            Dictionary of key/value (attribute name / attribute) pairs

        Returns
        -------
        variables : dict-like
        attributes : dict-like

        """
        variables = {k: self.encode_variable(v) for k, v in variables.items()}
        attributes = {k: self.encode_attribute(v) for k, v in attributes.items()}
        return variables, attributes

    def encode_variable(self, v):
        """encode one variable"""
        return v

    def encode_attribute(self, a):
        """encode one attribute"""
        return a

    def set_dimension(self, dim, length):  # pragma: no cover
        raise NotImplementedError()

    def set_attribute(self, k, v):  # pragma: no cover
        raise NotImplementedError()

    def set_variable(self, k, v):  # pragma: no cover
        raise NotImplementedError()

    def store_dataset(self, dataset):
        """
        in stores, variables are all variables AND coordinates
        in xarray.Dataset variables are variables NOT coordinates,
        so here we pass the whole dataset in instead of doing
        dataset.variables
        """
        self.store(dataset, dataset.attrs)

    def store(
        self,
        variables,
        attributes,
        check_encoding_set=frozenset(),
        writer=None,
        unlimited_dims=None,
    ):
        """
        Top level method for putting data on this store, this method:
          - encodes variables/attributes
          - sets dimensions
          - sets variables

        Parameters
        ----------
        variables : dict-like
            Dictionary of key/value (variable name / xr.Variable) pairs
        attributes : dict-like
            Dictionary of key/value (attribute name / attribute) pairs
        check_encoding_set : list-like
            List of variables that should be checked for invalid encoding
            values
        writer : ArrayWriter
        unlimited_dims : list-like
            List of dimension names that should be treated as unlimited
            dimensions.
        """
        if writer is None:
            writer = ArrayWriter()

        variables, attributes = self.encode(variables, attributes)

        self.set_attributes(attributes)
        self.set_dimensions(variables, unlimited_dims=unlimited_dims)
        self.set_variables(
            variables, check_encoding_set, writer, unlimited_dims=unlimited_dims
        )

    def set_attributes(self, attributes):
        """
        This provides a centralized method to set the dataset attributes on the
        data store.

        Parameters
        ----------
        attributes : dict-like
            Dictionary of key/value (attribute name / attribute) pairs
        """
        for k, v in attributes.items():
            self.set_attribute(k, v)

    def set_variables(self, variables, check_encoding_set, writer, unlimited_dims=None):
        """
        This provides a centralized method to set the variables on the data
        store.

        Parameters
        ----------
        variables : dict-like
            Dictionary of key/value (variable name / xr.Variable) pairs
        check_encoding_set : list-like
            List of variables that should be checked for invalid encoding
            values
        writer : ArrayWriter
        unlimited_dims : list-like
            List of dimension names that should be treated as unlimited
            dimensions.
        """

        for vn, v in variables.items():
            name = _encode_variable_name(vn)
            check = vn in check_encoding_set
            target, source = self.prepare_variable(
                name, v, check, unlimited_dims=unlimited_dims
            )

            writer.add(source, target)

    def set_dimensions(self, variables, unlimited_dims=None):
        """
        This provides a centralized method to set the dimensions on the data
        store.

        Parameters
        ----------
        variables : dict-like
            Dictionary of key/value (variable name / xr.Variable) pairs
        unlimited_dims : list-like
            List of dimension names that should be treated as unlimited
            dimensions.
        """
        if unlimited_dims is None:
            unlimited_dims = set()

        existing_dims = self.get_dimensions()

        dims = {}
        for v in unlimited_dims:  # put unlimited_dims first
            dims[v] = None
        for v in variables.values():
            dims.update(dict(zip(v.dims, v.shape)))

        for dim, length in dims.items():
            if dim in existing_dims and length != existing_dims[dim]:
                raise ValueError(
                    "Unable to update size for existing dimension"
                    "%r (%d != %d)" % (dim, length, existing_dims[dim])
                )
            elif dim not in existing_dims:
                is_unlimited = dim in unlimited_dims
                self.set_dimension(dim, length, is_unlimited)


class WritableCFDataStore(AbstractWritableDataStore):
    __slots__ = ()

    def encode(self, variables, attributes):
        """
        Encodes variables and attributes for NetCDF file writing.
        
        This function prepares variables and attributes for encoding in a NetCDF file. It first applies CF encoding to ensure compatibility, then encodes each variable and attribute using specific methods.
        
        Parameters:
        variables (dict): A dictionary where keys are variable names and values are variable data.
        attributes (dict): A dictionary where keys are attribute names and values are attribute data.
        
        Returns:
        tuple: A tuple containing two dictionaries:
        - The first dictionary contains
        """

        # All NetCDF files get CF encoded by default, without this attempting
        # to write times, for example, would fail.
        variables, attributes = cf_encoder(variables, attributes)
        variables = {k: self.encode_variable(v) for k, v in variables.items()}
        attributes = {k: self.encode_attribute(v) for k, v in attributes.items()}
        return variables, attributes


class BackendEntrypoint:
    """
    ``BackendEntrypoint`` is a class container and it is the main interface
    for the backend plugins, see :ref:`RST backend_entrypoint`.
    It shall implement:

    - ``open_dataset`` method: it shall implement reading from file, variables
      decoding and it returns an instance of :py:class:`~xarray.Dataset`.
      It shall take in input at least ``filename_or_obj`` argument and
      ``drop_variables`` keyword argument.
      For more details see :ref:`RST open_dataset`.
    - ``guess_can_open`` method: it shall return ``True`` if the backend is able to open
      ``filename_or_obj``, ``False`` otherwise. The implementation of this
      method is not mandatory.
    """

    open_dataset_parameters: Union[Tuple, None] = None
    """list of ``open_dataset`` method parameters"""

    def open_dataset(
        self,
        filename_or_obj: str,
        drop_variables: Tuple[str] = None,
        **kwargs: Any,
    ):
        """
        Backend open_dataset method used by Xarray in :py:func:`~xarray.open_dataset`.
        """

        raise NotImplementedError

    def guess_can_open(self, filename_or_obj):
        """
        Backend open_dataset method used by Xarray in :py:func:`~xarray.open_dataset`.
        """

        return False


BACKEND_ENTRYPOINTS: Dict[str, Type[BackendEntrypoint]] = {}
