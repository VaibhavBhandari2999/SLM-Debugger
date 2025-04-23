import copy

import numpy as np

from ..core.variable import Variable
from .common import AbstractWritableDataStore


class InMemoryDataStore(AbstractWritableDataStore):
    """
    Stores dimensions, variables and attributes in ordered dictionaries, making
    this store fast compared to stores which save to disk.

    This store exists purely for internal testing purposes.
    """

    def __init__(self, variables=None, attributes=None):
        self._variables = {} if variables is None else variables
        self._attributes = {} if attributes is None else attributes

    def get_attrs(self):
        return self._attributes

    def get_variables(self):
        return self._variables

    def get_dimensions(self):
        dims = {}
        for v in self._variables.values():
            for d, s in v.dims.items():
                dims[d] = s
        return dims

    def prepare_variable(self, k, v, *args, **kwargs):
        """
        Prepare a new Variable object for a given key and value.
        
        This function creates a new Variable object with the specified dimensions, initializes it with an empty array of the same type and shape as the input value, and associates it with the given key in the internal dictionary of variables. The function also returns the newly created Variable object and the data of the original value.
        
        Parameters:
        k (str): The key to associate the new Variable with in the internal dictionary.
        v (Variable): The original Variable
        """

        new_var = Variable(v.dims, np.empty_like(v), v.attrs)
        self._variables[k] = new_var
        return new_var, v.data

    def set_attribute(self, k, v):
        # copy to imitate writing to disk.
        self._attributes[k] = copy.deepcopy(v)

    def set_dimension(self, dim, length, unlimited_dims=None):
        # in this model, dimensions are accounted for in the variables
        pass
