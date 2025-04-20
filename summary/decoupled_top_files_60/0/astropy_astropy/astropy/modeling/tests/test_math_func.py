# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np
import pytest
from numpy.testing import assert_allclose

from astropy.modeling import math_functions

x = np.linspace(-20, 360, 100)


@pytest.mark.filterwarnings(r'ignore:.*:RuntimeWarning')
def test_math():
    """
    Test the math functions in astropy.modeling.math_functions.
    
    This function checks the correctness of the mathematical functions defined in
    the `astropy.modeling.math_functions` module. It iterates over all the
    functions in the module, creates an instance of each, and compares the output
    of the function with the corresponding NumPy function for the same operation.
    It also verifies that the `ModUfunc` and `DivideUfunc` are the same as
    `RemainderUfunc
    """

    for name in math_functions.__all__:
        model_class = getattr(math_functions, name)
        assert model_class.__module__ == 'astropy.modeling.math_functions'
        model = model_class()
        func = getattr(np, model.func.__name__)
        if model.n_inputs == 1:
            assert_allclose(model(x), func(x))
        elif model.n_inputs == 2:
            assert_allclose(model(x, x), func(x, x))

    assert math_functions.ModUfunc is math_functions.RemainderUfunc
    assert math_functions.DivideUfunc is math_functions.True_divideUfunc
