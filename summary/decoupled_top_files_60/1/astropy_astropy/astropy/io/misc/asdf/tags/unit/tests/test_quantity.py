# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest

asdf = pytest.importorskip("asdf")

import io

from asdf.tests import helpers

from astropy import units


def roundtrip_quantity(yaml, quantity):
    """
    Convert a YAML string to an ASDF file, roundtrip the ASDF file, and verify the quantity array.
    
    This function takes a YAML string and a quantity array, converts the YAML string to an ASDF file, checks if the quantity array in the ASDF file matches the input array, writes the ASDF file to a buffer, and then reads it back to verify the roundtrip process.
    
    Parameters:
    yaml (str): The YAML string to be converted to an ASDF file.
    """

    buff = helpers.yaml_to_asdf(yaml)
    with asdf.open(buff) as ff:
        assert (ff.tree["quantity"] == quantity).all()
        buff2 = io.BytesIO()
        ff.write_to(buff2)

    buff2.seek(0)
    with asdf.open(buff2) as ff:
        assert (ff.tree["quantity"] == quantity).all()


def test_value_scalar(tmpdir):
    """
    Test that a scalar value with a unit can be correctly serialized and deserialized using YAML.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object provided by pytest for creating temporary files.
    
    Returns:
    None: This function does not return anything. It tests the serialization and deserialization of a `Quantity` object with a scalar value and a unit.
    """

    testval = 2.71828
    testunit = units.kpc
    yaml = f"""
quantity: !unit/quantity-1.1.0
    value: {testval}
    unit: {testunit}
"""

    quantity = units.Quantity(testval, unit=testunit)
    roundtrip_quantity(yaml, quantity)


def test_value_array(tmpdir):
    testval = [3.14159]
    testunit = units.kg
    yaml = f"""
quantity: !unit/quantity-1.1.0
    value: !core/ndarray-1.0.0 {testval}
    unit: {testunit}
"""

    quantity = units.Quantity(testval, unit=testunit)
    roundtrip_quantity(yaml, quantity)


def test_value_multiarray(tmpdir):
    testval = [x * 2.3081 for x in range(10)]
    testunit = units.ampere
    yaml = f"""
quantity: !unit/quantity-1.1.0
    value: !core/ndarray-1.0.0 {testval}
    unit: {testunit}
"""

    quantity = units.Quantity(testval, unit=testunit)
    roundtrip_quantity(yaml, quantity)


def test_value_ndarray(tmpdir):
    from numpy import array, float64

    testval = [[1, 2, 3], [4, 5, 6]]
    testunit = units.km
    yaml = f"""
quantity: !unit/quantity-1.1.0
    value: !core/ndarray-1.0.0
        datatype: float64
        data:
            {testval}
    unit: {testunit}
"""

    data = array(testval, float64)
    quantity = units.Quantity(data, unit=testunit)
    roundtrip_quantity(yaml, quantity)
ay(testval, float64)
    quantity = units.Quantity(data, unit=testunit)
    roundtrip_quantity(yaml, quantity)
