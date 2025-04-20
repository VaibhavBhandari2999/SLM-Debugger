# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np

from astropy import units as u
from astropy.modeling.core import Model, fix_inputs
from astropy.modeling.models import Polynomial1D


class _ExampleModel(Model):
    n_inputs = 1
    n_outputs = 1

    def __init__(self):
        """
        Initialize the object with input and return units.
        
        This method sets up the object with the specified input and return units.
        
        Parameters:
        None
        
        Attributes:
        _input_units (dict): A dictionary containing the units of the input parameters. Currently set to {'x': u.m}.
        _return_units (dict): A dictionary containing the units of the return values. Currently set to {'y': u.m/u.s}.
        
        Inherited Methods:
        This method calls the superclass's __init__ method
        """

        self._input_units = {"x": u.m}
        self._return_units = {"y": u.m/u.s}
        super().__init__()

    def evaluate(self, input):
        return input / u.Quantity(1, u.s)


def _models_with_units():
    """
    Generate a list of models with associated units.
    
    This function returns a list of models, each with associated input and output units. The models include combinations of basic models and polynomial models, with some models fixed at specific input values.
    
    Parameters:
    None
    
    Returns:
    list: A list of tuples, each containing a model, its input units, and its return units.
    - models (list): A list of `astropy.modeling.Model` instances.
    - input_units (list): A
    """

    m1 = _ExampleModel() & _ExampleModel()
    m2 = _ExampleModel() + _ExampleModel()
    p = Polynomial1D(1)
    p._input_units = {'x': u.m / u.s}
    p._return_units = {'y': u.m / u.s}
    m3 = _ExampleModel() | p
    m4 = fix_inputs(m1, {'x0': 1})
    m5 = fix_inputs(m1, {0: 1})

    models = [m1, m2, m3, m4, m5]
    input_units = [{'x0': u.Unit("m"), 'x1': u.Unit("m")},
                   {'x': u.Unit("m")},
                   {'x': u.Unit("m")},
                   {'x1': u.Unit("m")},
                   {'x1': u.Unit("m")}
                   ]

    return_units = [{'y0': u.Unit("m / s"), 'y1': u.Unit("m / s")},
                    {'y': u.Unit("m / s")},
                    {'y': u.Unit("m / s")},
                    {'y0': u.Unit("m / s"), 'y1': u.Unit("m / s")},
                    {'y0': u.Unit("m / s"), 'y1': u.Unit("m / s")}
                    ]
    return np.array([models, input_units, return_units], dtype=object).T


@pytest.mark.parametrize(("model", "input_units", "return_units"), _models_with_units())
def test_input_units(model, input_units, return_units):
    """ Test input_units on various compound models."""
    assert model.input_units == input_units
    assert model.return_units == return_units
