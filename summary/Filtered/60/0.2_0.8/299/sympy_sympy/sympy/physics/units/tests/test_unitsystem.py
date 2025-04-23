from sympy.physics.units import DimensionSystem, joule, second, ampere

from sympy.core.numbers import Rational
from sympy.core.singleton import S
from sympy.physics.units.definitions import c, kg, m, s
from sympy.physics.units.definitions.dimension_definitions import length, time
from sympy.physics.units.quantities import Quantity
from sympy.physics.units.unitsystem import UnitSystem
from sympy.physics.units.util import convert_to


def test_definition():
    # want to test if the system can have several units of the same dimension
    dm = Quantity("dm")
    base = (m, s)
    # base_dim = (m.dimension, s.dimension)
    ms = UnitSystem(base, (c, dm), "MS", "MS system")
    ms.set_quantity_dimension(dm, length)
    ms.set_quantity_scale_factor(dm, Rational(1, 10))

    assert set(ms._base_units) == set(base)
    assert set(ms._units) == {m, s, c, dm}
    # assert ms._units == DimensionSystem._sort_dims(base + (velocity,))
    assert ms.name == "MS"
    assert ms.descr == "MS system"


def test_str_repr():
    """
    Test the string and representation (repr) methods of the UnitSystem class.
    
    This function checks the output of the `str` and `repr` functions for the UnitSystem class. It ensures that the string representation correctly formats the unit system with or without a name, and that the representation method returns a formatted string indicating the units in the system.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Assertions:
    - The string representation of a UnitSystem with a name ('MS') should be 'MS'.
    """

    assert str(UnitSystem((m, s), name="MS")) == "MS"
    assert str(UnitSystem((m, s))) == "UnitSystem((meter, second))"

    assert repr(UnitSystem((m, s))) == "<UnitSystem: (%s, %s)>" % (m, s)


def test_convert_to():
    """
    Convert a Quantity to a specified unit system.
    
    This function converts a given Quantity to the base units of a specified unit system.
    
    Parameters:
    quantity (Quantity): The Quantity to be converted.
    target_units (tuple): A tuple containing the base units of the target unit system.
    
    Returns:
    Quantity: The converted Quantity expressed in the target unit system's base units.
    """

    A = Quantity("A")
    A.set_global_relative_scale_factor(S.One, ampere)

    Js = Quantity("Js")
    Js.set_global_relative_scale_factor(S.One, joule*second)

    mksa = UnitSystem((m, kg, s, A), (Js,))
    assert convert_to(Js, mksa._base_units) == m**2*kg*s**-1/1000


def test_extend():
    ms = UnitSystem((m, s), (c,))
    Js = Quantity("Js")
    Js.set_global_relative_scale_factor(1, joule*second)
    mks = ms.extend((kg,), (Js,))

    res = UnitSystem((m, s, kg), (c, Js))
    assert set(mks._base_units) == set(res._base_units)
    assert set(mks._units) == set(res._units)


def test_dim():
    dimsys = UnitSystem((m, kg, s), (c,))
    assert dimsys.dim == 3


def test_is_consistent():
    dimension_system = DimensionSystem([length, time])
    us = UnitSystem([m, s], dimension_system=dimension_system)
    assert us.is_consistent == True


def test_get_units_non_prefixed():
    from sympy.physics.units import volt, ohm
    unit_system = UnitSystem.get_unit_system("SI")
    units = unit_system.get_units_non_prefixed()
    for prefix in ["giga", "tera", "peta", "exa", "zetta", "yotta", "kilo", "hecto", "deca", "deci", "centi", "milli", "micro", "nano", "pico", "femto", "atto", "zepto", "yocto"]:
        for unit in units:
            assert isinstance(unit, Quantity), f"{unit} must be a Quantity, not {type(unit)}"
            assert not unit.is_prefixed, f"{unit} is marked as prefixed"
            assert not unit.is_physical_constant, f"{unit} is marked as physics constant"
            assert not unit.name.name.startswith(prefix), f"Unit {unit.name} has prefix {prefix}"
    assert volt in units
    assert ohm in units

def test_derived_units_must_exist_in_unit_system():
    for unit_system in UnitSystem._unit_systems.values():
        for preferred_unit in unit_system.derived_units.values():
            units = preferred_unit.atoms(Quantity)
            for unit in units:
                assert unit in unit_system._units, f"Unit {unit} is not in unit system {unit_system}"
hat are part of the system.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If a derived unit is found that is not in the unit system.
    
    This function iterates over all unit systems and ensures that each derived unit is composed of base units that are defined within the same system.
    """

    for unit_system in UnitSystem._unit_systems.values():
        for preferred_unit in unit_system.derived_units.values():
            units = preferred_unit.atoms(Quantity)
            for unit in units:
                assert unit in unit_system._units, f"Unit {unit} is not in unit system {unit_system}"
