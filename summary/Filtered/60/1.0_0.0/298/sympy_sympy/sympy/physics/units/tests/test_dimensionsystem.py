from sympy.core.symbol import symbols
from sympy.matrices.dense import (Matrix, eye)
from sympy.physics.units.definitions.dimension_definitions import (
    action, current, length, mass, time,
    velocity)
from sympy.physics.units.dimensions import DimensionSystem


def test_extend():
    """
    Extend a dimension system with additional base dimensions and derived dimensions.
    
    This function takes an existing dimension system and extends it by adding new base dimensions and corresponding derived dimensions.
    
    Parameters:
    ms (DimensionSystem): The original dimension system to be extended.
    base_dims (tuple): A tuple of new base dimensions to be added.
    derived_dims (tuple): A tuple of new derived dimensions to be added.
    
    Returns:
    DimensionSystem: The extended dimension system with the new base and derived dimensions.
    """

    ms = DimensionSystem((length, time), (velocity,))

    mks = ms.extend((mass,), (action,))

    res = DimensionSystem((length, time, mass), (velocity, action))
    assert mks.base_dims == res.base_dims
    assert mks.derived_dims == res.derived_dims


def test_list_dims():
    dimsys = DimensionSystem((length, time, mass))

    assert dimsys.list_can_dims == (length, mass, time)


def test_dim_can_vector():
    """
    Generate the canonical vector for a given dimension in the dimension system.
    
    This function computes the canonical vector corresponding to a given dimension within a specified dimension system.
    
    Parameters:
    dim (Dimension): The dimension for which the canonical vector is to be computed.
    
    Returns:
    Matrix: The canonical vector corresponding to the given dimension.
    
    Example:
    >>> dimsys = DimensionSystem([length, mass, time], [velocity, action], {velocity: {length: 1, time: -1}})
    >>>
    """

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
    mksa = DimensionSystem(
        (length, time, mass, current),
        (action,),
        {action: {mass: 1, length: 2, time: -1}})
    L, M, T = symbols("L M T")
    assert mksa.print_dim_base(action) == L**2*M/T


def test_dim():
    """
    Test the dimension system to determine the number of dimensions.
    
    This function checks the dimension system to ensure it correctly identifies the number of dimensions based on the given base dimensions, derived dimensions, and their corresponding dimensionality.
    
    Parameters:
    None
    
    Returns:
    int: The number of dimensions in the dimension system.
    
    Notes:
    - The function uses a predefined `DimensionSystem` object with specified base dimensions and derived dimensions.
    - It verifies that the dimension system correctly calculates the number of dimensions.
    """

    dimsys = DimensionSystem(
        (length, mass, time),
        (velocity, action),
        {velocity: {length: 1, time: -1},
         action: {mass: 1, length: 2, time: -1}}
    )
    assert dimsys.dim == 3
