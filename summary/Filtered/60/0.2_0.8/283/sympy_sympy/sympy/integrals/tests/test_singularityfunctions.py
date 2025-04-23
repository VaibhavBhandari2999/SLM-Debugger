from sympy.integrals.singularityfunctions import singularityintegrate
from sympy import SingularityFunction, symbols, Function

x, a, n, y = symbols('x a n y')
f = Function('f')


def test_singularityintegrate():
    """
    Test the integration of SingularityFunction.
    
    This function tests the integration of SingularityFunction with respect to the variable x. It checks for the integration of a SingularityFunction with a constant, a linear combination of SingularityFunction, and the integration involving a variable and a SingularityFunction.
    
    Parameters:
    - x: The variable of integration.
    - a: The point of singularity for SingularityFunction.
    
    Returns:
    - None if the integration involves a singularity.
    - The integrated SingularityFunction otherwise
    """

    assert singularityintegrate(x, x) is None
    assert singularityintegrate(x + SingularityFunction(x, 9, 1), x) is None

    assert 4*singularityintegrate(SingularityFunction(x, a, 3), x) == 4*SingularityFunction(x, a, 4)/4
    assert singularityintegrate(5*SingularityFunction(x, 5, -2), x) == 5*SingularityFunction(x, 5, -1)
    assert singularityintegrate(6*SingularityFunction(x, 5, -1), x) == 6*SingularityFunction(x, 5, 0)
    assert singularityintegrate(x*SingularityFunction(x, 0, -1), x) == 0
    assert singularityintegrate((x - 5)*SingularityFunction(x, 5, -1), x) == 0
    assert singularityintegrate(SingularityFunction(x, 0, -1) * f(x), x) == f(0) * SingularityFunction(x, 0, 0)
    assert singularityintegrate(SingularityFunction(x, 1, -1) * f(x), x) == f(1) * SingularityFunction(x, 1, 0)
    assert singularityintegrate(y*SingularityFunction(x, 0, -1)**2, x) == \
        y*SingularityFunction(0, 0, -1)*SingularityFunction(x, 0, 0)
