from sympy.core.symbol import symbols
from sympy.matrices.dense import (Matrix, eye)
from sympy.physics.units.definitions.dimension_definitions import (
    action, current, length, mass, time,
    velocity)
from sympy.physics.units.dimensions import DimensionSystem


def test_extend():
    ms = DimensionSystem((length, time), (velocity,))

    mks = ms.extend((mass,), (action,))

    res = DimensionSystem((length, time, mass), (velocity, action))
    assert mks.base_dims == res.base_dims
    assert mks.derived_dims == res.derived_dims


def test_list_dims():
    """
    Function to test the list of canonical dimensions in a DimensionSystem.
    
    This function checks the list of canonical dimensions in a given DimensionSystem.
    
    Parameters:
    dimsys (DimensionSystem): The DimensionSystem object to be tested.
    
    Returns:
    tuple: A tuple containing the list of canonical dimensions in the DimensionSystem.
    """

    dimsys = DimensionSystem((length, time, mass))

    assert dimsys.list_can_dims == (length, mass, time)


def test_dim_can_vector():
    dimsys = DimensionSystem(
        [length, mass, time],
        [velocity, action],
        {
            velocity: {length: 1, time: -1}
        }
    )

    assert dimsys.dim_can_vector(length) == Matrix([1, 0, 0])
    assert dimsys.dim_can_vector(velocity) == Matrix([1, 0, -1])

    dimsys = DimensionSystem(
        (length, velocity, action),
        (mass, time),
        {
            time: {length: 1, velocity: -1}
        }
    )

    assert dimsys.dim_can_vector(length) == Matrix([0, 1, 0])
    assert dimsys.dim_can_vector(velocity) == Matrix([0, 0, 1])
    assert dimsys.dim_can_vector(time) == Matrix([0, 1, -1])

    dimsys = DimensionSystem(
        (length, mass, time),
        (velocity, action),
        {velocity: {length: 1, time: -1},
         action: {mass: 1, length: 2, time: -1}})

    assert dimsys.dim_vector(length) == Matrix([1, 0, 0])
    assert dimsys.dim_vector(velocity) == Matrix([1, 0, -1])


def test_inv_can_transf_matrix():
    dimsys = DimensionSystem((length, mass, time))
    assert dimsys.inv_can_transf_matrix == eye(3)


def test_can_transf_matrix():
    dimsys = DimensionSystem((length, mass, time))
    assert dimsys.can_transf_matrix == eye(3)

    dimsys = DimensionSystem((length, velocity, action))
    assert dimsys.can_transf_matrix == eye(3)

    dimsys = DimensionSystem((length, time), (velocity,), {velocity: {length: 1, time: -1}})
    assert dimsys.can_transf_matrix == eye(2)


def test_is_consistent():
    assert DimensionSystem((length, time)).is_consistent is True


def test_print_dim_base():
    """
    Print the base dimension of the given action in the specified DimensionSystem.
    
    Parameters:
    action (Symbol): The action for which the base dimension is to be printed.
    
    Returns:
    str: The base dimension of the action in terms of the fundamental dimensions (length, mass, time, etc.).
    
    Example:
    >>> L, M, T = symbols('L M T')
    >>> mksa = DimensionSystem((length, time, mass, current), (action,), {action: {mass
    """

    mksa = DimensionSystem(
        (length, time, mass, current),
        (action,),
        {action: {mass: 1, length: 2, time: -1}})
    L, M, T = symbols("L M T")
    assert mksa.print_dim_base(action) == L**2*M/T


def test_dim():
    dimsys = DimensionSystem(
        (length, mass, time),
        (velocity, action),
        {velocity: {length: 1, time: -1},
         action: {mass: 1, length: 2, time: -1}}
    )
    assert dimsys.dim == 3
