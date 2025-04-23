from sympy import (Eq, Matrix, pi, sin, sqrt, Symbol, Integral, Piecewise,
    symbols, Float, I)
from mpmath import mnorm, mpf
from sympy.solvers import nsolve
from sympy.utilities.lambdify import lambdify
from sympy.utilities.pytest import raises, XFAIL
from sympy.utilities.decorator import conserve_mpmath_dps

@XFAIL
def test_nsolve_fail():
    x = symbols('x')
    # Sometimes it is better to use the numerator (issue 4829)
    # but sometimes it is not (issue 11768) so leave this to
    # the discretion of the user
    ans = nsolve(x**2/(1 - x)/(1 - 2*x)**2 - 100, x, 0)
    assert ans > 0.46 and ans < 0.47


def test_nsolve_denominator():
    """
    Test that nsolve correctly handles the full expression, including the denominator.
    
    Parameters:
    x (Symbol): The symbol for the variable in the expression.
    
    Returns:
    float: The numerical solution to the equation, avoiding division by zero.
    
    Example:
    >>> x = symbols('x')
    >>> ans = test_nsolve_denominator()
    >>> ans
    -1.0
    """

    x = symbols('x')
    # Test that nsolve uses the full expression (numerator and denominator).
    ans = nsolve((x**2 + 3*x + 2)/(x + 2), -2.1)
    # The root -2 was divided out, so make sure we don't find it.
    assert ans == -1.0

def test_nsolve():
    # onedimensional
    x = Symbol('x')
    assert nsolve(sin(x), 2) - pi.evalf() < 1e-15
    assert nsolve(Eq(2*x, 2), x, -10) == nsolve(2*x - 2, -10)
    # Testing checks on number of inputs
    raises(TypeError, lambda: nsolve(Eq(2*x, 2)))
    raises(TypeError, lambda: nsolve(Eq(2*x, 2), x, 1, 2))
    # multidimensional
    x1 = Symbol('x1')
    x2 = Symbol('x2')
    f1 = 3 * x1**2 - 2 * x2**2 - 1
    f2 = x1**2 - 2 * x1 + x2**2 + 2 * x2 - 8
    f = Matrix((f1, f2)).T
    F = lambdify((x1, x2), f.T, modules='mpmath')
    for x0 in [(-1, 1), (1, -2), (4, 4), (-4, -4)]:
        x = nsolve(f, (x1, x2), x0, tol=1.e-8)
        assert mnorm(F(*x), 1) <= 1.e-10
    # The Chinese mathematician Zhu Shijie was the very first to solve this
    # nonlinear system 700 years ago (z was added to make it 3-dimensional)
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    f1 = -x + 2*y
    f2 = (x**2 + x*(y**2 - 2) - 4*y) / (x + 4)
    f3 = sqrt(x**2 + y**2)*z
    f = Matrix((f1, f2, f3)).T
    F = lambdify((x, y, z), f.T, modules='mpmath')

    def getroot(x0):
        """
        getroot(x0)
        Compute the root of a multivariable function F(x, y, z) using numerical methods.
        
        Parameters:
        x0 (float): Initial guess for the root.
        
        Returns:
        tuple: The root of the function F(x, y, z) as a tuple (x, y, z).
        
        Notes:
        - The function F is defined elsewhere and should be a multivariable function of x, y, and z.
        - The root is found using
        """

        root = nsolve(f, (x, y, z), x0)
        assert mnorm(F(*root), 1) <= 1.e-8
        return root
    assert list(map(round, getroot((1, 1, 1)))) == [2.0, 1.0, 0.0]
    assert nsolve([Eq(
        f1), Eq(f2), Eq(f3)], [x, y, z], (1, 1, 1))  # just see that it works
    a = Symbol('a')
    assert abs(nsolve(1/(0.001 + a)**3 - 6/(0.9 - a)**3, a, 0.3) -
        mpf('0.31883011387318591')) < 1e-15



def test_issue_6408():
    x = Symbol('x')
    assert nsolve(Piecewise((x, x < 1), (x**2, True)), x, 2) == 0.0


@XFAIL
def test_issue_6408_fail():
    x, y = symbols('x y')
    assert nsolve(Integral(x*y, (x, 0, 5)), y, 2) == 0.0


@conserve_mpmath_dps
def test_increased_dps():
    """
    Test increased dps.
    
    This function tests the numerical solving capabilities of the mpmath library
    with increased decimal precision. It sets the decimal precision to 128, defines
    a symbolic equation, and solves it numerically. The function returns the
    numerical solution and checks its accuracy against the expected value.
    
    Parameters:
    None
    
    Returns:
    q (float): The numerical solution of the equation x^2 - pi = 0, computed
    with 128 decimal precision
    """

    # Issue 8564
    import mpmath
    mpmath.mp.dps = 128
    x = Symbol('x')
    e1 = x**2 - pi
    q = nsolve(e1, x, 3.0)

    assert abs(sqrt(pi).evalf(128) - q) < 1e-128

def test_nsolve_precision():
    x, y = symbols('x y')
    sol = nsolve(x**2 - pi, x, 3, prec=128)
    assert abs(sqrt(pi).evalf(128) - sol) < 1e-128
    assert isinstance(sol, Float)

    sols = nsolve((y**2 - x, x**2 - pi), (x, y), (3, 3), prec=128)
    assert isinstance(sols, Matrix)
    assert sols.shape == (2, 1)
    assert abs(sqrt(pi).evalf(128) - sols[0]) < 1e-128
    assert abs(sqrt(sqrt(pi)).evalf(128) - sols[1]) < 1e-128
    assert all(isinstance(i, Float) for i in sols)

def test_nsolve_complex():
    """
    Test the nsolve function for complex numbers.
    
    This function tests the nsolve function from SymPy for finding roots of complex numbers and systems of equations involving complex numbers.
    
    Parameters:
    x, y (Symbol): Symbols representing complex variables.
    
    Returns:
    The solution to the equation or system of equations as a complex number or a matrix of complex numbers.
    
    Key Points:
    - nsolve(x**2 + 2, 1j) returns sqrt(2)*I
    - nsolve(x**2 +
    """

    x, y = symbols('x y')

    assert nsolve(x**2 + 2, 1j) == sqrt(2.)*I
    assert nsolve(x**2 + 2, I) == sqrt(2.)*I

    assert nsolve([x**2 + 2, y**2 + 2], [x, y], [I, I]) == Matrix([sqrt(2.)*I, sqrt(2.)*I])
    assert nsolve([x**2 + 2, y**2 + 2], [x, y], [I, I]) == Matrix([sqrt(2.)*I, sqrt(2.)*I])

def test_nsolve_dict_kwarg():
    x, y = symbols('x y')
    # one variable
    assert nsolve(x**2 - 2, 1, dict = True) == \
        [{x: sqrt(2.)}]
    # one variable with complex solution
    assert nsolve(x**2 + 2, I, dict = True) == \
        [{x: sqrt(2.)*I}]
    # two variables
    assert nsolve([x**2 + y**2 - 5, x**2 - y**2 + 1], [x, y], [1, 1], dict = True) == \
        [{x: sqrt(2.), y: sqrt(3.)}]
