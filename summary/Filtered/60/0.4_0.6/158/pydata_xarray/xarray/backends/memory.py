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
        Prepare a new variable for assignment or manipulation.
        
        This function creates a new Variable object with the same dimensions and attributes as the input variable `v`. The new variable is then stored in the `_variables` dictionary using the key `k`. The original data of `v` is returned alongside the newly created variable.
        
        Parameters:
        k (str): The key under which the new variable will be stored in the `_variables` dictionary.
        v (Variable): The input variable whose dimensions and attributes are used
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
ted for in the variables
        pass
