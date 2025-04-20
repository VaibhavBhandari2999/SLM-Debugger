from sympy import (S, Symbol, Sum, I, lambdify, re, im, log, simplify, sqrt,
                   zeta, pi, besseli, Dummy, oo, Piecewise, Rational, beta,
                   floor)
from sympy.core.relational import Eq, Ne
from sympy.functions.elementary.exponential import exp
from sympy.logic.boolalg import Or
from sympy.sets.fancysets import Range
from sympy.stats import (P, E, variance, density, characteristic_function,
                         where, moment_generating_function, skewness, cdf)
from sympy.stats.drv_types import (PoissonDistribution, GeometricDistribution,
                                   Poisson, Geometric, Logarithmic, NegativeBinomial, Skellam,
                                   YuleSimon, Zeta)
from sympy.stats.rv import sample
from sympy.utilities.pytest import slow, nocache_fail

x = Symbol('x')


def test_PoissonDistribution():
    """
    Test the Poisson distribution.
    
    Args:
    l (float): The rate parameter of the Poisson distribution.
    
    Returns:
    None: This function performs assertions to check the correctness of the Poisson distribution implementation.
    """

    l = 3
    p = PoissonDistribution(l)
    assert abs(p.cdf(10).evalf() - 1) < .001
    assert p.expectation(x, x) == l
    assert p.expectation(x**2, x) - p.expectation(x, x)**2 == l


def test_Poisson():
    """
    Test the Poisson distribution.
    
    This function tests the Poisson distribution with a specified rate parameter `l`.
    It creates a random variable `x` following a Poisson distribution with rate `l`.
    The function checks the expected value (mean) and variance of the distribution,
    as well as the density function, ensuring they match the theoretical properties
    of the Poisson distribution. It also verifies that the expressions for the
    expected values of `x` and `2*x` are correctly represented as Sum objects
    """

    l = 3
    x = Poisson('x', l)
    assert E(x) == l
    assert variance(x) == l
    assert density(x) == PoissonDistribution(l)
    assert isinstance(E(x, evaluate=False), Sum)
    assert isinstance(E(2*x, evaluate=False), Sum)


def test_GeometricDistribution():
    p = S.One / 5
    d = GeometricDistribution(p)
    assert d.expectation(x, x) == 1/p
    assert d.expectation(x**2, x) - d.expectation(x, x)**2 == (1-p)/p**2
    assert abs(d.cdf(20000).evalf() - 1) < .001


def test_Logarithmic():
    """
    Test the Logarithmic distribution.
    
    Parameters
    ----------
    p : float
    Probability of success (0 < p < 1).
    
    Returns
    -------
    None
    This function does not return any value. It is used to check the expected behavior of the Logarithmic distribution.
    
    Notes
    -----
    This function checks the expected behavior of the Logarithmic distribution by evaluating the expected value, variance, and a transformed expression. The results are compared to the expected values.
    """

    p = S.Half
    x = Logarithmic('x', p)
    assert E(x) == -p / ((1 - p) * log(1 - p))
    assert variance(x) == -1/log(2)**2 + 2/log(2)
    assert E(2*x**2 + 3*x + 4) == 4 + 7 / log(2)
    assert isinstance(E(x, evaluate=False), Sum)


@nocache_fail
def test_negative_binomial():
    """
    Test the properties of a Negative Binomial random variable.
    
    Parameters:
    r (int): The number of successes until the experiment is stopped.
    p (float): The probability of success in each trial.
    
    Returns:
    None: This function does not return any value. It prints the expected value and variance of the Negative Binomial distribution, as well as the result of a more complex expression involving the random variable.
    
    Key Properties:
    - Expected Value (E(x)): p*r / (1-p
    """

    r = 5
    p = S.One / 3
    x = NegativeBinomial('x', r, p)
    assert E(x) == p*r / (1-p)
    # This hangs when run with the cache disabled:
    assert variance(x) == p*r / (1-p)**2
    assert E(x**5 + 2*x + 3) == Rational(9207, 4)
    assert isinstance(E(x, evaluate=False), Sum)


def test_skellam():
    mu1 = Symbol('mu1')
    mu2 = Symbol('mu2')
    z = Symbol('z')
    X = Skellam('x', mu1, mu2)

    assert density(X)(z) == (mu1/mu2)**(z/2) * \
        exp(-mu1 - mu2)*besseli(z, 2*sqrt(mu1*mu2))
    assert skewness(X).expand() == mu1/(mu1*sqrt(mu1 + mu2) + mu2 *
                sqrt(mu1 + mu2)) - mu2/(mu1*sqrt(mu1 + mu2) + mu2*sqrt(mu1 + mu2))
    assert variance(X).expand() == mu1 + mu2
    assert E(X) == mu1 - mu2
    assert characteristic_function(X)(z) == exp(
        mu1*exp(I*z) - mu1 - mu2 + mu2*exp(-I*z))
    assert moment_generating_function(X)(z) == exp(
        mu1*exp(z) - mu1 - mu2 + mu2*exp(-z))


def test_yule_simon():
    from sympy import S
    rho = S(3)
    x = YuleSimon('x', rho)
    assert simplify(E(x)) == rho / (rho - 1)
    assert simplify(variance(x)) == rho**2 / ((rho - 1)**2 * (rho - 2))
    assert isinstance(E(x, evaluate=False), Sum)
    # To test the cdf function
    assert cdf(x)(x) == Piecewise((-beta(floor(x), 4)*floor(x) + 1, x >= 1), (0, True))


def test_zeta():
    """
    Test the Zeta distribution.
    
    This function evaluates the expected value and variance of a Zeta
    distribution with parameter `s`. The Zeta distribution is parameterized
    by a single positive real number `s`.
    
    Parameters
    ----------
    s : float or SymPy symbol
    The shape parameter of the Zeta distribution.
    
    Returns
    -------
    expected_value : float or SymPy expression
    The expected value of the distribution.
    variance : float or SymPy expression
    The variance of the distribution.
    """

    s = S(5)
    x = Zeta('x', s)
    assert E(x) == zeta(s-1) / zeta(s)
    assert simplify(variance(x)) == (
        zeta(s) * zeta(s-2) - zeta(s-1)**2) / zeta(s)**2


@slow
def test_sample_discrete():
    X, Y, Z = Geometric('X', S.Half), Poisson('Y', 4), Poisson('Z', 1000)
    W = Poisson('W', Rational(1, 100))
    assert sample(X) in X.pspace.domain.set
    assert sample(Y) in Y.pspace.domain.set
    assert sample(Z) in Z.pspace.domain.set
    assert sample(W) in W.pspace.domain.set


def test_discrete_probability():
    X = Geometric('X', Rational(1, 5))
    Y = Poisson('Y', 4)
    G = Geometric('e', x)
    assert P(Eq(X, 3)) == Rational(16, 125)
    assert P(X < 3) == Rational(9, 25)
    assert P(X > 3) == Rational(64, 125)
    assert P(X >= 3) == Rational(16, 25)
    assert P(X <= 3) == Rational(61, 125)
    assert P(Ne(X, 3)) == Rational(109, 125)
    assert P(Eq(Y, 3)) == 32*exp(-4)/3
    assert P(Y < 3) == 13*exp(-4)
    assert P(Y > 3).equals(32*(Rational(-71, 32) + 3*exp(4)/32)*exp(-4)/3)
    assert P(Y >= 3).equals(32*(Rational(-39, 32) + 3*exp(4)/32)*exp(-4)/3)
    assert P(Y <= 3) == 71*exp(-4)/3
    assert P(Ne(Y, 3)).equals(
        13*exp(-4) + 32*(Rational(-71, 32) + 3*exp(4)/32)*exp(-4)/3)
    assert P(X < S.Infinity) is S.One
    assert P(X > S.Infinity) is S.Zero
    assert P(G < 3) == x*(2-x)
    assert P(Eq(G, 3)) == x*(-x + 1)**2


def test_precomputed_characteristic_functions():
    """
    Test the precomputed characteristic functions of various discrete distributions.
    
    This function verifies the correctness of the precomputed characteristic
    functions for several discrete distributions by comparing them with the
    Fourier transform of the corresponding probability density functions.
    
    Parameters:
    dist (Distribution): The discrete distribution for which the characteristic
    function is to be tested.
    support_lower_limit (float): The lower limit of the support of the distribution.
    support_upper_limit (float): The upper limit of the support of the distribution.
    
    The
    """

    import mpmath

    def test_cf(dist, support_lower_limit, support_upper_limit):
        """
        Validate the characteristic function (CF) of a given probability distribution.
        
        This function compares the characteristic function of a specified probability
        distribution with the Fourier transform of its probability density function (PDF).
        The comparison is performed at several test points to ensure the two functions
        match.
        
        Parameters:
        dist (Distribution): The probability distribution for which the characteristic
        function is to be validated.
        support_lower_limit (float): The lower limit of the support of the distribution.
        support_upper_limit (float): The
        """

        pdf = density(dist)
        t = S('t')
        x = S('x')

        # first function is the hardcoded CF of the distribution
        cf1 = lambdify([t], characteristic_function(dist)(t), 'mpmath')

        # second function is the Fourier transform of the density function
        f = lambdify([x, t], pdf(x)*exp(I*x*t), 'mpmath')
        cf2 = lambda t: mpmath.nsum(lambda x: f(x, t), [
            support_lower_limit, support_upper_limit], maxdegree=10)

        # compare the two functions at various points
        for test_point in [2, 5, 8, 11]:
            n1 = cf1(test_point)
            n2 = cf2(test_point)

            assert abs(re(n1) - re(n2)) < 1e-12
            assert abs(im(n1) - im(n2)) < 1e-12

    test_cf(Geometric('g', Rational(1, 3)), 1, mpmath.inf)
    test_cf(Logarithmic('l', Rational(1, 5)), 1, mpmath.inf)
    test_cf(NegativeBinomial('n', 5, Rational(1, 7)), 0, mpmath.inf)
    test_cf(Poisson('p', 5), 0, mpmath.inf)
    test_cf(YuleSimon('y', 5), 1, mpmath.inf)
    test_cf(Zeta('z', 5), 1, mpmath.inf)


def test_moment_generating_functions():
    """
    Tests for moment generating functions.
    
    This function evaluates the moment generating functions (MGFs) for various discrete distributions at specific points and checks their derivatives at zero. The distributions tested include Geometric, Logarithmic, NegativeBinomial, Poisson, Skellam, YuleSimon, and Zeta. The function verifies that the first derivative of each MGF at t=0 matches the expected value for each distribution.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Distributions and Expected Values
    """

    t = S('t')

    geometric_mgf = moment_generating_function(Geometric('g', S.Half))(t)
    assert geometric_mgf.diff(t).subs(t, 0) == 2

    logarithmic_mgf = moment_generating_function(Logarithmic('l', S.Half))(t)
    assert logarithmic_mgf.diff(t).subs(t, 0) == 1/log(2)

    negative_binomial_mgf = moment_generating_function(
        NegativeBinomial('n', 5, Rational(1, 3)))(t)
    assert negative_binomial_mgf.diff(t).subs(t, 0) == Rational(5, 2)

    poisson_mgf = moment_generating_function(Poisson('p', 5))(t)
    assert poisson_mgf.diff(t).subs(t, 0) == 5

    skellam_mgf = moment_generating_function(Skellam('s', 1, 1))(t)
    assert skellam_mgf.diff(t).subs(
        t, 2) == (-exp(-2) + exp(2))*exp(-2 + exp(-2) + exp(2))

    yule_simon_mgf = moment_generating_function(YuleSimon('y', 3))(t)
    assert simplify(yule_simon_mgf.diff(t).subs(t, 0)) == Rational(3, 2)

    zeta_mgf = moment_generating_function(Zeta('z', 5))(t)
    assert zeta_mgf.diff(t).subs(t, 0) == pi**4/(90*zeta(5))


def test_Or():
    X = Geometric('X', S.Half)
    P(Or(X < 3, X > 4)) == Rational(13, 16)
    P(Or(X > 2, X > 1)) == P(X > 1)
    P(Or(X >= 3, X < 3)) == 1


def test_where():
    """
    Test the 'where' function for specific conditions on random variables.
    
    This function evaluates the 'where' function for given conditions on two random variables, X and Y. X is a geometric random variable with a success probability of 1/5, and Y is a Poisson random variable with a mean of 4.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    1. Evaluates the condition X**2 > 4 and returns the range of values for X that satisfy this condition.
    """

    X = Geometric('X', Rational(1, 5))
    Y = Poisson('Y', 4)
    assert where(X**2 > 4).set == Range(3, S.Infinity, 1)
    assert where(X**2 >= 4).set == Range(2, S.Infinity, 1)
    assert where(Y**2 < 9).set == Range(0, 3, 1)
    assert where(Y**2 <= 9).set == Range(0, 4, 1)


def test_conditional():
    X = Geometric('X', Rational(2, 3))
    Y = Poisson('Y', 3)
    assert P(X > 2, X > 3) == 1
    assert P(X > 3, X > 2) == Rational(1, 3)
    assert P(Y > 2, Y < 2) == 0
    assert P(Eq(Y, 3), Y >= 0) == 9*exp(-3)/2
    assert P(Eq(Y, 3), Eq(Y, 2)) == 0
    assert P(X < 2, Eq(X, 2)) == 0
    assert P(X > 2, Eq(X, 3)) == 1


def test_product_spaces():
    X1 = Geometric('X1', S.Half)
    X2 = Geometric('X2', Rational(1, 3))
    #assert str(P(X1 + X2 < 3, evaluate=False)) == """Sum(Piecewise((2**(X2 - n - 2)*(2/3)**(X2 - 1)/6, """\
    #    + """(-X2 + n + 3 >= 1) & (-X2 + n + 3 < oo)), (0, True)), (X2, 1, oo), (n, -oo, -1))"""
    n = Dummy('n')
    assert P(X1 + X2 < 3, evaluate=False).dummy_eq(Sum(Piecewise((2**(-n)/4,
         n + 2 >= 1), (0, True)), (n, -oo, -1))/3)
    #assert str(P(X1 + X2 > 3)) == """Sum(Piecewise((2**(X2 - n - 2)*(2/3)**(X2 - 1)/6, """ +\
    #    """(-X2 + n + 3 >= 1) & (-X2 + n + 3 < oo)), (0, True)), (X2, 1, oo), (n, 1, oo))"""
    assert P(X1 + X2 > 3).dummy_eq(Sum(Piecewise((2**(X2 - n - 2)*(Rational(2, 3))**(X2 - 1)/6,
                                                 -X2 + n + 3 >= 1), (0, True)),
                                       (X2, 1, oo), (n, 1, oo)))
#    assert str(P(Eq(X1 + X2, 3))) == """Sum(Piecewise((2**(X2 - 2)*(2/3)**(X2 - 1)/6, """ +\
#        """X2 <= 2), (0, True)), (X2, 1, oo))"""
    assert P(Eq(X1 + X2, 3)) == Rational(1, 12)
