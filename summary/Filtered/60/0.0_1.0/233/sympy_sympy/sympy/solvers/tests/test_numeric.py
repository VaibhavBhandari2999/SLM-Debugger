from sympy import (Eq, Matrix, pi, sin, sqrt, Symbol, Integral, Piecewise,
    symbols, Float, I)
from mpmath import mnorm, mpf
from sympy.solvers import nsolve
from sympy.utilities.lambdify import lambdify
from sympy.utilities.pytest import raises, XFAIL
from sympy.utilities.decorator import conserve_mpmath_dps

@XFAIL
def test_nsolve_fail():
    """
    Test the nsolve function with a specific equation and initial guess.
    
    Parameters:
    x (Symbol): The symbol for the variable in the equation.
    
    Returns:
    float: The numerical solution for the variable x that satisfies the equation.
    
    Notes:
    - The function uses the `nsolve` method to find the numerical solution.
    - The equation being solved is x**2 / (1 - x) / (1 - 2*x)**2 - 100.
    - The initial guess for the solution is
    """

    x = symbols('x')
    # Sometimes it is better to use the numerator (issue 4829)
    # but sometimes it is not (issue 11768) so leave this to
    # the discretion of the user
    ans = nsolve(x**2/(1 - x)/(1 - 2*x)**2 - 100, x, 0)
    assert ans > 0.46 and ans < 0.47


def test_nsolve_denominator():
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
        Find a root of the function f near the initial guess x0.
        
        Parameters:
        x0 (float): Initial guess for the root.
        
        Returns:
        tuple: A tuple containing the root of the function.
        
        Raises:
        AssertionError: If the norm of the function evaluated at the root is greater than 1e-8.
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
    # Issue 8564
    import mpmath
    mpmath.mp.dps = 128
    x = Symbol('x')
    e1 = x**2 - pi
    q = nsolve(e1, x, 3.0)

    assert abs(sqrt(pi).evalf(128) - q) < 1e-128

def test_nsolve_precision():
    """
    Test the precision of nsolve for a single equation and a system of equations.
    
    This function checks the precision of the nsolve function for solving a single equation and a system of equations. It uses a specified precision level and verifies the solution against known values.
    
    Parameters:
    - x, y (Symbols): The symbols used in the equations.
    - prec (int): The precision level for the nsolve function.
    
    Returns:
    - None: The function asserts the correctness of the solutions and does not return any value
    """

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
    x, y = symbols('x y')

    assert nsolve(x**2 + 2, 1j) == sqrt(2.)*I
    assert nsolve(x**2 + 2, I) == sqrt(2.)*I

    assert nsolve([x**2 + 2, y**2 + 2], [x, y], [I, I]) == Matrix([sqrt(2.)*I, sqrt(2.)*I])
    assert nsolve([x**2 + 2, y**2 + 2], [x, y], [I, I]) == Matrix([sqrt(2.)*I, sqrt(2.)*I])

def test_nsolve_dict_kwarg():
    """
    Solve an equation or a system of equations numerically and return the solution as a dictionary.
    
    This function takes an equation or a system of equations and an initial guess, and returns the numerical solution as a dictionary. The solution can be for one or more variables.
    
    Parameters:
    - eqns: A single equation or a list of equations.
    - init_guess: A single value or a list of values representing the initial guess for the solution.
    - dict: A boolean flag indicating whether to
    """

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
