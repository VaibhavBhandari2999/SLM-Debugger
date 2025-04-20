from sympy import (
    nan, pi, symbols, DiracDelta, Symbol, diff,
    Piecewise, I, Eq, Derivative, oo, SingularityFunction, Heaviside,
    Float
)

from sympy.core.expr import unchanged
from sympy.core.function import ArgumentIndexError
from sympy.testing.pytest import raises

x, y, a, n = symbols('x y a n')


def test_fdiff():
    """
    Test the differentiation of SingularityFunction.
    
    This function checks the differentiation of SingularityFunction with respect to a variable. It verifies that the differentiation of SingularityFunction at a point with a given exponent follows the expected rules. The function also tests the differentiation of SingularityFunction with respect to a variable and with multiple differentiations.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The function asserts that the first derivative of SingularityFunction at a point with a given exponent is equal to
    """

    assert SingularityFunction(x, 4, 5).fdiff() == 5*SingularityFunction(x, 4, 4)
    assert SingularityFunction(x, 4, -1).fdiff() == SingularityFunction(x, 4, -2)
    assert SingularityFunction(x, 4, 0).fdiff() == SingularityFunction(x, 4, -1)

    assert SingularityFunction(y, 6, 2).diff(y) == 2*SingularityFunction(y, 6, 1)
    assert SingularityFunction(y, -4, -1).diff(y) == SingularityFunction(y, -4, -2)
    assert SingularityFunction(y, 4, 0).diff(y) == SingularityFunction(y, 4, -1)
    assert SingularityFunction(y, 4, 0).diff(y, 2) == SingularityFunction(y, 4, -2)

    n = Symbol('n', positive=True)
    assert SingularityFunction(x, a, n).fdiff() == n*SingularityFunction(x, a, n - 1)
    assert SingularityFunction(y, a, n).diff(y) == n*SingularityFunction(y, a, n - 1)

    expr_in = 4*SingularityFunction(x, a, n) + 3*SingularityFunction(x, a, -1) + -10*SingularityFunction(x, a, 0)
    expr_out = n*4*SingularityFunction(x, a, n - 1) + 3*SingularityFunction(x, a, -2) - 10*SingularityFunction(x, a, -1)
    assert diff(expr_in, x) == expr_out

    assert SingularityFunction(x, -10, 5).diff(evaluate=False) == (
        Derivative(SingularityFunction(x, -10, 5), x))

    raises(ArgumentIndexError, lambda: SingularityFunction(x, 4, 5).fdiff(2))


def test_eval():
    """
    Test the SingularityFunction for correctness.
    
    This function evaluates the SingularityFunction for various inputs and checks
    if the output is as expected. It also ensures that the function behaves
    correctly with different parameters and edge cases.
    
    Parameters:
    - x: The variable at which the SingularityFunction is evaluated.
    - a: The point of the singularity.
    - n: The order of the singularity.
    
    Returns:
    - The result of the SingularityFunction for the given inputs.
    
    Raises:
    - ValueError
    """

    assert SingularityFunction(x, a, n).func == SingularityFunction
    assert unchanged(SingularityFunction, x, 5, n)
    assert SingularityFunction(5, 3, 2) == 4
    assert SingularityFunction(3, 5, 1) == 0
    assert SingularityFunction(3, 3, 0) == 1
    assert SingularityFunction(4, 4, -1) is oo
    assert SingularityFunction(4, 2, -1) == 0
    assert SingularityFunction(4, 7, -1) == 0
    assert SingularityFunction(5, 6, -2) == 0
    assert SingularityFunction(4, 2, -2) == 0
    assert SingularityFunction(4, 4, -2) is oo
    assert (SingularityFunction(6.1, 4, 5)).evalf(5) == Float('40.841', '5')
    assert SingularityFunction(6.1, pi, 2) == (-pi + 6.1)**2
    assert SingularityFunction(x, a, nan) is nan
    assert SingularityFunction(x, nan, 1) is nan
    assert SingularityFunction(nan, a, n) is nan

    raises(ValueError, lambda: SingularityFunction(x, a, I))
    raises(ValueError, lambda: SingularityFunction(2*I, I, n))
    raises(ValueError, lambda: SingularityFunction(x, a, -3))


def test_rewrite():
    """
    Rewrite SingularityFunction in terms of other functions.
    
    This function converts a SingularityFunction into its equivalent form using
    Piecewise, Heaviside, and DiracDelta functions.
    
    Parameters:
    x (Symbol): The variable in the singularity function.
    a (float or Symbol): The point of singularity.
    n (int or Symbol): The power of the singularity function.
    
    Returns:
    Expr: The equivalent form of the SingularityFunction in terms of
    Piecewise
    """

    assert SingularityFunction(x, 4, 5).rewrite(Piecewise) == (
        Piecewise(((x - 4)**5, x - 4 > 0), (0, True)))
    assert SingularityFunction(x, -10, 0).rewrite(Piecewise) == (
        Piecewise((1, x + 10 > 0), (0, True)))
    assert SingularityFunction(x, 2, -1).rewrite(Piecewise) == (
        Piecewise((oo, Eq(x - 2, 0)), (0, True)))
    assert SingularityFunction(x, 0, -2).rewrite(Piecewise) == (
        Piecewise((oo, Eq(x, 0)), (0, True)))

    n = Symbol('n', nonnegative=True)
    assert SingularityFunction(x, a, n).rewrite(Piecewise) == (
        Piecewise(((x - a)**n, x - a > 0), (0, True)))

    expr_in = SingularityFunction(x, 4, 5) + SingularityFunction(x, -3, -1) - SingularityFunction(x, 0, -2)
    expr_out = (x - 4)**5*Heaviside(x - 4) + DiracDelta(x + 3) - DiracDelta(x, 1)
    assert expr_in.rewrite(Heaviside) == expr_out
    assert expr_in.rewrite(DiracDelta) == expr_out
    assert expr_in.rewrite('HeavisideDiracDelta') == expr_out

    expr_in = SingularityFunction(x, a, n) + SingularityFunction(x, a, -1) - SingularityFunction(x, a, -2)
    expr_out = (x - a)**n*Heaviside(x - a) + DiracDelta(x - a) + DiracDelta(a - x, 1)
    assert expr_in.rewrite(Heaviside) == expr_out
    assert expr_in.rewrite(DiracDelta) == expr_out
    assert expr_in.rewrite('HeavisideDiracDelta') == expr_out
