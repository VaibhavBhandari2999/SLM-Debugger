from sympy.integrals.singularityfunctions import singularityintegrate
from sympy import SingularityFunction, symbols, Function

x, a, n, y = symbols('x a n y')
f = Function('f')


def test_singularityintegrate():
    """
    Test the integration of SingularityFunction objects.
    
    Parameters:
    - x: The variable of integration.
    - a: The point of the singularity.
    - f(x): A function multiplied with the SingularityFunction.
    
    Returns:
    - The integrated SingularityFunction or a simplified expression.
    
    Key Points:
    - The function handles integration of SingularityFunction objects.
    - It supports integration with a variable and a singularity point.
    - It can handle SingularityFunction objects multiplied by other functions.
    - The function returns None
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
