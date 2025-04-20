from sympy import Piecewise, lambdify, Equality, Unequality, Sum, Mod, cbrt, sqrt
from sympy.abc import x, i, j, a, b, c, d
from sympy.codegen.cfunctions import log1p, expm1, hypot, log10, exp2, log2, Cbrt, Sqrt
from sympy.printing.lambdarepr import NumPyPrinter

from sympy.utilities.pytest import skip
from sympy.external import import_module

np = import_module('numpy')

def test_numpy_piecewise_regression():
    """
    NumPyPrinter needs to print Piecewise()'s choicelist as a list to avoid
    breaking compatibility with numpy 1.8. This is not necessary in numpy 1.9+.
    See gh-9747 and gh-9749 for details.
    """
    p = Piecewise((1, x < 0), (0, True))
    assert NumPyPrinter().doprint(p) == 'numpy.select([numpy.less(x, 0),True], [1,0], default=numpy.nan)'


def test_sum():
    """
    Test the sum function using NumPy.
    
    This function checks the correctness of the sum function for symbolic summation
    using SymPy and numerical evaluation with NumPy.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `skip` from nose to skip the test if NumPy is not installed.
    - It tests two cases of symbolic summation:
    1. Sum of powers of x from a to b.
    2. Sum of i * x from
    """

    if not np:
        skip("NumPy not installed")

    s = Sum(x ** i, (i, a, b))
    f = lambdify((a, b, x), s, 'numpy')

    a_, b_ = 0, 10
    x_ = np.linspace(-1, +1, 10)
    assert np.allclose(f(a_, b_, x_), sum(x_ ** i_ for i_ in range(a_, b_ + 1)))

    s = Sum(i * x, (i, a, b))
    f = lambdify((a, b, x), s, 'numpy')

    a_, b_ = 0, 10
    x_ = np.linspace(-1, +1, 10)
    assert np.allclose(f(a_, b_, x_), sum(i_ * x_ for i_ in range(a_, b_ + 1)))


def test_multiple_sums():
    if not np:
        skip("NumPy not installed")

    s = Sum((x + j) * i, (i, a, b), (j, c, d))
    f = lambdify((a, b, c, d, x), s, 'numpy')

    a_, b_ = 0, 10
    c_, d_ = 11, 21
    x_ = np.linspace(-1, +1, 10)
    assert np.allclose(f(a_, b_, c_, d_, x_),
                       sum((x_ + j_) * i_ for i_ in range(a_, b_ + 1) for j_ in range(c_, d_ + 1)))


def test_relational():
    """
    Generate a Python function to evaluate various relational operations on a NumPy array.
    
    This function creates a lambda function to evaluate different relational operations on a given NumPy array. The operations include equality, inequality, less than, less than or equal to, greater than, and greater than or equal to. The function returns a NumPy array of boolean values indicating the result of each operation for each element in the input array.
    
    Parameters:
    x (Symbol): The input symbolic variable.
    
    Returns:
    np.ndarray
    """

    if not np:
        skip("NumPy not installed")

    e = Equality(x, 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [False, True, False])

    e = Unequality(x, 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [True, False, True])

    e = (x < 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [True, False, False])

    e = (x <= 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [True, True, False])

    e = (x > 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [False, False, True])

    e = (x >= 1)

    f = lambdify((x,), e)
    x_ = np.array([0, 1, 2])
    assert np.array_equal(f(x_), [False, True, True])


def test_mod():
    if not np:
        skip("NumPy not installed")

    e = Mod(a, b)
    f = lambdify((a, b), e)

    a_ = np.array([0, 1, 2, 3])
    b_ = 2
    assert np.array_equal(f(a_, b_), [0, 1, 0, 1])

    a_ = np.array([0, 1, 2, 3])
    b_ = np.array([2, 2, 2, 2])
    assert np.array_equal(f(a_, b_), [0, 1, 0, 1])

    a_ = np.array([2, 3, 4, 5])
    b_ = np.array([2, 3, 4, 5])
    assert np.array_equal(f(a_, b_), [0, 0, 0, 0])


def test_expm1():
    if not np:
        skip("NumPy not installed")

    f = lambdify((a,), expm1(a), 'numpy')
    assert abs(f(1e-10) - 1e-10 - 5e-21) < 1e-22


def test_log1p():
    if not np:
        skip("NumPy not installed")

    f = lambdify((a,), log1p(a), 'numpy')
    assert abs(f(1e-99) - 1e-99) < 1e-100

def test_hypot():
    """
    Test the hypot function from the numpy library.
    
    Parameters:
    a (array-like): The first input for the hypot function.
    b (array-like): The second input for the hypot function.
    
    This function checks if the NumPy library is installed. If not, it skips the test. Otherwise, it uses the `lambdify` function to create a callable function from the `hypot` function and evaluates it with inputs (3, 4). The result is compared
    """

    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a, b), hypot(a, b), 'numpy')(3, 4) - 5) < 1e-16

def test_log10():
    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a,), log10(a), 'numpy')(100) - 2) < 1e-16


def test_exp2():
    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a,), exp2(a), 'numpy')(5) - 32) < 1e-16


def test_log2():
    """
    Test the log2 function from the math library using NumPy for numerical computation.
    
    Parameters:
    a (float): The input value for which the log2 will be computed.
    
    Returns:
    float: The computed log2 value of the input.
    
    Notes:
    This function uses NumPy for numerical computation and skips the test if NumPy is not installed.
    """

    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a,), log2(a), 'numpy')(256) - 8) < 1e-16


def test_Sqrt():
    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a,), Sqrt(a), 'numpy')(4) - 2) < 1e-16


def test_sqrt():
    """
    Test the square root function using NumPy.
    
    This function checks if NumPy is installed and skips the test if it is not.
    It then uses the `lambdify` function from SymPy to create a NumPy-compatible
    function for computing the square root of a given number and asserts that
    the result is within a very small tolerance (1e-16) of the expected value (2)
    for the input 4.
    """

    if not np:
        skip("NumPy not installed")
    assert abs(lambdify((a,), sqrt(a), 'numpy')(4) - 2) < 1e-16
