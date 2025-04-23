from sympy.concrete.tests.test_sums_products import NS

from sympy import sqrt, S
from sympy.physics.units import convert_to, coulomb_constant, elementary_charge, gravitational_constant, planck
from sympy.physics.units.definitions.unit_definitions import statcoulomb, coulomb, second, gram, centimeter, erg, \
    newton, joule, dyne, speed_of_light, meter
from sympy.physics.units.systems import SI
from sympy.physics.units.systems.cgs import cgs_gauss


def test_conversion_to_from_si():
    """
    Test conversion between units in different systems.
    
    This function tests the conversion between units in the CGS-Gauss and SI systems, including special cases for electromagnetism.
    
    Parameters:
    - convert_to (Quantity): The quantity to be converted.
    - to_unit (str or Quantity): The unit to convert to.
    - system (str): The system of units to use for conversion ('cgs_gauss' or 'SI').
    
    Returns:
    - Quantity: The converted quantity.
    
    Key Notes
    """


    assert convert_to(statcoulomb, coulomb, cgs_gauss) == 5*coulomb/149896229
    assert convert_to(coulomb, statcoulomb, cgs_gauss) == 149896229*statcoulomb/5
    assert convert_to(statcoulomb, sqrt(gram*centimeter**3)/second, cgs_gauss) == centimeter**(S(3)/2)*sqrt(gram)/second
    assert convert_to(coulomb, sqrt(gram*centimeter**3)/second, cgs_gauss) == 149896229*centimeter**(S(3)/2)*sqrt(gram)/(5*second)

    # SI units have an additional base unit, no conversion in case of electromagnetism:
    assert convert_to(coulomb, statcoulomb, SI) == coulomb
    assert convert_to(statcoulomb, coulomb, SI) == statcoulomb

    # SI without electromagnetism:
    assert convert_to(erg, joule, SI) == joule/10**7
    assert convert_to(erg, joule, cgs_gauss) == joule/10**7
    assert convert_to(joule, erg, SI) == 10**7*erg
    assert convert_to(joule, erg, cgs_gauss) == 10**7*erg

    assert convert_to(dyne, newton, SI) == newton/10**5
    assert convert_to(dyne, newton, cgs_gauss) == newton/10**5
    assert convert_to(newton, dyne, SI) == 10**5*dyne
    assert convert_to(newton, dyne, cgs_gauss) == 10**5*dyne


def test_cgs_gauss_convert_constants():
    """
    Convert physical constants between CGS-Gaussian and SI units.
    
    This function is used to convert the values of physical constants between the CGS-Gaussian system and the SI system.
    
    Parameters:
    constant (Quantity): The physical constant to be converted.
    to_system (str): The target system of units for the conversion ('cgs_gauss' or 'SI').
    
    Returns:
    Quantity: The converted value of the physical constant in the target system of units.
    """


    assert convert_to(speed_of_light, centimeter/second, cgs_gauss) == 29979245800*centimeter/second

    assert convert_to(coulomb_constant, 1, cgs_gauss) == 1
    assert convert_to(coulomb_constant, newton*meter**2/coulomb**2, cgs_gauss) == 22468879468420441*meter**2*newton/(25000000000*coulomb**2)
    assert convert_to(coulomb_constant, newton*meter**2/coulomb**2, SI) == 22468879468420441*meter**2*newton/(2500000*coulomb**2)
    assert convert_to(coulomb_constant, dyne*centimeter**2/statcoulomb**2, cgs_gauss) == centimeter**2*dyne/statcoulomb**2
    assert convert_to(coulomb_constant, 1, SI) == coulomb_constant
    assert NS(convert_to(coulomb_constant, newton*meter**2/coulomb**2, SI)) == '8987551787.36818*meter**2*newton/coulomb**2'

    assert convert_to(elementary_charge, statcoulomb, cgs_gauss)
    assert convert_to(gravitational_constant, dyne*centimeter**2/gram**2, cgs_gauss)
    assert NS(convert_to(planck, erg*second, cgs_gauss)) == '6.62607015e-27*erg*second'
