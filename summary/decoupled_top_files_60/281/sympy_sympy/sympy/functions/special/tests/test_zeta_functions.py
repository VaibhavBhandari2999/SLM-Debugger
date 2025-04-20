from sympy import (Symbol, zeta, nan, Rational, Float, pi, dirichlet_eta, log,
                   zoo, expand_func, polylog, lerchphi, S, exp, sqrt, I,
                   exp_polar, polar_lift, O, stieltjes, Abs, Sum, oo)
from sympy.core.function import ArgumentIndexError
from sympy.functions.combinatorial.numbers import bernoulli, factorial
from sympy.testing.pytest import raises
from sympy.testing.randtest import (test_derivative_numerically as td,
                      random_complex_number as randcplx, verify_numerically as tn)

x = Symbol('x')
a = Symbol('a')
b = Symbol('b', negative=True)
z = Symbol('z')
s = Symbol('s')


def test_zeta_eval():
    """
    Test the evaluation of the Riemann zeta function.
    
    This function checks the evaluation of the Riemann zeta function, `zeta(s)`, for various inputs, including special cases and series shifts. It verifies the function's behavior for different values of `s` and `x` (the shift parameter), and ensures correct handling of special cases such as `0`, `1`, and `oo`.
    
    Key Parameters:
    - `s`: The complex or real number for which the z
    """


    assert zeta(nan) is nan
    assert zeta(x, nan) is nan

    assert zeta(0) == Rational(-1, 2)
    assert zeta(0, x) == S.Half - x
    assert zeta(0, b) == S.Half - b

    assert zeta(1) is zoo
    assert zeta(1, 2) is zoo
    assert zeta(1, -7) is zoo
    assert zeta(1, x) is zoo

    assert zeta(2, 1) == pi**2/6

    assert zeta(2) == pi**2/6
    assert zeta(4) == pi**4/90
    assert zeta(6) == pi**6/945

    assert zeta(2, 2) == pi**2/6 - 1
    assert zeta(4, 3) == pi**4/90 - Rational(17, 16)
    assert zeta(6, 4) == pi**6/945 - Rational(47449, 46656)

    assert zeta(2, -2) == pi**2/6 + Rational(5, 4)
    assert zeta(4, -3) == pi**4/90 + Rational(1393, 1296)
    assert zeta(6, -4) == pi**6/945 + Rational(3037465, 2985984)

    assert zeta(oo) == 1

    assert zeta(-1) == Rational(-1, 12)
    assert zeta(-2) == 0
    assert zeta(-3) == Rational(1, 120)
    assert zeta(-4) == 0
    assert zeta(-5) == Rational(-1, 252)

    assert zeta(-1, 3) == Rational(-37, 12)
    assert zeta(-1, 7) == Rational(-253, 12)
    assert zeta(-1, -4) == Rational(119, 12)
    assert zeta(-1, -9) == Rational(539, 12)

    assert zeta(-4, 3) == -17
    assert zeta(-4, -8) == 8772

    assert zeta(0, 1) == Rational(-1, 2)
    assert zeta(0, -1) == Rational(3, 2)

    assert zeta(0, 2) == Rational(-3, 2)
    assert zeta(0, -2) == Rational(5, 2)

    assert zeta(
        3).evalf(20).epsilon_eq(Float("1.2020569031595942854", 20), 1e-19)


def test_zeta_series():
    assert zeta(x, a).series(a, 0, 2) == \
        zeta(x, 0) - x*a*zeta(x + 1, 0) + O(a**2)


def test_dirichlet_eta_eval():

    assert dirichlet_eta(0) == S.Half
    assert dirichlet_eta(-1) == Rational(1, 4)
    assert dirichlet_eta(1) == log(2)
    assert dirichlet_eta(2) == pi**2/12
    assert dirichlet_eta(4) == pi**4*Rational(7, 720)


def test_rewriting():
    """
    Rewrite the Dirichlet eta function and Riemann zeta function in terms of each other and other related functions.
    
    This function performs the following transformations:
    - Rewrites the Dirichlet eta function in terms of the Riemann zeta function and vice versa.
    - Rewrites the Riemann zeta function with a general parameter 'a' in terms of the Dirichlet eta function.
    - Rewrites the Lerch phi function in terms of the Riemann zeta function
    """

    assert dirichlet_eta(x).rewrite(zeta) == (1 - 2**(1 - x))*zeta(x)
    assert zeta(x).rewrite(dirichlet_eta) == dirichlet_eta(x)/(1 - 2**(1 - x))
    assert zeta(x).rewrite(dirichlet_eta, a=2) == zeta(x)
    assert tn(dirichlet_eta(x), dirichlet_eta(x).rewrite(zeta), x)
    assert tn(zeta(x), zeta(x).rewrite(dirichlet_eta), x)

    assert zeta(x, a).rewrite(lerchphi) == lerchphi(1, x, a)
    assert polylog(s, z).rewrite(lerchphi) == lerchphi(z, s, 1)*z

    assert lerchphi(1, x, a).rewrite(zeta) == zeta(x, a)
    assert z*lerchphi(z, s, 1).rewrite(polylog) == polylog(s, z)


def test_derivatives():
    from sympy import Derivative
    assert zeta(x, a).diff(x) == Derivative(zeta(x, a), x)
    assert zeta(x, a).diff(a) == -x*zeta(x + 1, a)
    assert lerchphi(
        z, s, a).diff(z) == (lerchphi(z, s - 1, a) - a*lerchphi(z, s, a))/z
    assert lerchphi(z, s, a).diff(a) == -s*lerchphi(z, s + 1, a)
    assert polylog(s, z).diff(z) == polylog(s - 1, z)/z

    b = randcplx()
    c = randcplx()
    assert td(zeta(b, x), x)
    assert td(polylog(b, z), z)
    assert td(lerchphi(c, b, x), x)
    assert td(lerchphi(x, b, c), x)
    raises(ArgumentIndexError, lambda: lerchphi(c, b, x).fdiff(2))
    raises(ArgumentIndexError, lambda: lerchphi(c, b, x).fdiff(4))
    raises(ArgumentIndexError, lambda: polylog(b, z).fdiff(1))
    raises(ArgumentIndexError, lambda: polylog(b, z).fdiff(3))


def myexpand(func, target):
    expanded = expand_func(func)
    if target is not None:
        return expanded == target
    if expanded == func:  # it didn't expand
        return False

    # check to see that the expanded and original evaluate to the same value
    subs = {}
    for a in func.free_symbols:
        subs[a] = randcplx()
    return abs(func.subs(subs).n()
               - expanded.replace(exp_polar, exp).subs(subs).n()) < 1e-10


def test_polylog_expansion():
    """
    Test the polylogarithm function for specific values and expansions.
    
    This function checks the polylogarithm function for specific values and verifies the correctness of its expansions for different parameters.
    
    Parameters:
    s (sympy.Symbol): The order of the polylogarithm.
    z (sympy.Symbol): The argument of the polylogarithm.
    
    Returns:
    None: This function does not return any value. It prints the results of the checks.
    
    Key Checks:
    1. polylog
    """

    from sympy import log
    assert polylog(s, 0) == 0
    assert polylog(s, 1) == zeta(s)
    assert polylog(s, -1) == -dirichlet_eta(s)
    assert polylog(s, exp_polar(I*pi*Rational(4, 3))) == polylog(s, exp(I*pi*Rational(4, 3)))
    assert polylog(s, exp_polar(I*pi)/3) == polylog(s, exp(I*pi)/3)

    assert myexpand(polylog(1, z), -log(1 - z))
    assert myexpand(polylog(0, z), z/(1 - z))
    assert myexpand(polylog(-1, z), z/(1 - z)**2)
    assert ((1-z)**3 * expand_func(polylog(-2, z))).simplify() == z*(1 + z)
    assert myexpand(polylog(-5, z), None)


def test_issue_8404():
    """
    Test the convergence of the sum of the series 1/(3*i + 1)**2 from i=0 to infinity.
    
    Parameters:
    None
    
    Returns:
    bool: True if the absolute value of the difference between the computed sum and 1.122 is less than 0.001, otherwise False.
    
    Key Concepts:
    - i: Symbol representing the integer index of the series.
    - Sum: The summation of the series from i=0 to infinity
    """

    i = Symbol('i', integer=True)
    assert Abs(Sum(1/(3*i + 1)**2, (i, 0, S.Infinity)).doit().n(4)
        - 1.122) < 0.001


def test_polylog_values():
    from sympy.testing.randtest import verify_numerically as tn
    assert polylog(2, 2) == pi**2/4 - I*pi*log(2)
    assert polylog(2, S.Half) == pi**2/12 - log(2)**2/2
    for z in [S.Half, 2, (sqrt(5)-1)/2, -(sqrt(5)-1)/2, -(sqrt(5)+1)/2, (3-sqrt(5))/2]:
        assert Abs(polylog(2, z).evalf() - polylog(2, z, evaluate=False).evalf()) < 1e-15
    z = Symbol("z")
    for s in [-1, 0]:
        for _ in range(10):
            assert tn(polylog(s, z), polylog(s, z, evaluate=False), z,
                a=-3, b=-2, c=S.Half, d=2)
            assert tn(polylog(s, z), polylog(s, z, evaluate=False), z,
                a=2, b=-2, c=5, d=2)

    from sympy import Integral
    assert polylog(0, Integral(1, (x, 0, 1))) == -S.Half


def test_lerchphi_expansion():
    """
    Test the Lerch Phi function expansion.
    
    This function checks the expansion of the Lerch Phi function (lerchphi) into
    known functions or series. It verifies the expansion for different values of
    the parameters and handles cases where direct summation or reduction to other
    functions (like polylogarithm or Hurwitz zeta) is applicable.
    
    Parameters:
    z (sympy expression): The argument of the Lerch Phi function.
    s (sympy expression): The exponent
    """

    assert myexpand(lerchphi(1, s, a), zeta(s, a))
    assert myexpand(lerchphi(z, s, 1), polylog(s, z)/z)

    # direct summation
    assert myexpand(lerchphi(z, -1, a), a/(1 - z) + z/(1 - z)**2)
    assert myexpand(lerchphi(z, -3, a), None)
    # polylog reduction
    assert myexpand(lerchphi(z, s, S.Half),
                    2**(s - 1)*(polylog(s, sqrt(z))/sqrt(z)
                              - polylog(s, polar_lift(-1)*sqrt(z))/sqrt(z)))
    assert myexpand(lerchphi(z, s, 2), -1/z + polylog(s, z)/z**2)
    assert myexpand(lerchphi(z, s, Rational(3, 2)), None)
    assert myexpand(lerchphi(z, s, Rational(7, 3)), None)
    assert myexpand(lerchphi(z, s, Rational(-1, 3)), None)
    assert myexpand(lerchphi(z, s, Rational(-5, 2)), None)

    # hurwitz zeta reduction
    assert myexpand(lerchphi(-1, s, a),
                    2**(-s)*zeta(s, a/2) - 2**(-s)*zeta(s, (a + 1)/2))
    assert myexpand(lerchphi(I, s, a), None)
    assert myexpand(lerchphi(-I, s, a), None)
    assert myexpand(lerchphi(exp(I*pi*Rational(2, 5)), s, a), None)


def test_stieltjes():
    assert isinstance(stieltjes(x), stieltjes)
    assert isinstance(stieltjes(x, a), stieltjes)

    # Zero'th constant EulerGamma
    assert stieltjes(0) == S.EulerGamma
    assert stieltjes(0, 1) == S.EulerGamma

    # Not defined
    assert stieltjes(nan) is nan
    assert stieltjes(0, nan) is nan
    assert stieltjes(-1) is S.ComplexInfinity
    assert stieltjes(1.5) is S.ComplexInfinity
    assert stieltjes(z, 0) is S.ComplexInfinity
    assert stieltjes(z, -1) is S.ComplexInfinity


def test_stieltjes_evalf():
    assert abs(stieltjes(0).evalf() - 0.577215664) < 1E-9
    assert abs(stieltjes(0, 0.5).evalf() - 1.963510026) < 1E-9
    assert abs(stieltjes(1, 2).evalf() + 0.072815845 ) < 1E-9


def test_issue_10475():
    """
    Test the finite nature of the Riemann zeta function for different inputs.
    
    This function evaluates the finite nature of the Riemann zeta function for various symbolic inputs. The Riemann zeta function is considered finite if the result is a finite number, and non-finite if the result is infinite or undefined.
    
    Parameters:
    a (Symbol): A symbolic variable representing a real number.
    b (Symbol): A symbolic variable representing a positive number.
    s (Symbol): A symbolic
    """

    a = Symbol('a', extended_real=True)
    b = Symbol('b', extended_positive=True)
    s = Symbol('s', zero=False)

    assert zeta(2 + I).is_finite
    assert zeta(1).is_finite is False
    assert zeta(x).is_finite is None
    assert zeta(x + I).is_finite is None
    assert zeta(a).is_finite is None
    assert zeta(b).is_finite is None
    assert zeta(-b).is_finite is True
    assert zeta(b**2 - 2*b + 1).is_finite is None
    assert zeta(a + I).is_finite is True
    assert zeta(b + 1).is_finite is True
    assert zeta(s + 1).is_finite is True


def test_issue_14177():
    n = Symbol('n', positive=True, integer=True)

    assert zeta(2*n) == (-1)**(n + 1)*2**(2*n - 1)*pi**(2*n)*bernoulli(2*n)/factorial(2*n)
    assert zeta(-n) == (-1)**(-n)*bernoulli(n + 1)/(n + 1)

    n = Symbol('n')

    assert zeta(2*n) == zeta(2*n) # As sign of z (= 2*n) is not determined
