from sympy import symbols, oo, Sum, harmonic, Add, S, binomial, factorial
from sympy.series.limitseq import limit_seq
from sympy.series.limitseq import difference_delta as dd
from sympy.utilities.pytest import raises, XFAIL

n, m, k = symbols('n m k', integer=True)


def test_difference_delta():
    """
    Test the difference delta of expressions e and e2 with respect to the variable n.
    
    Parameters:
    e (expression): The first expression.
    e2 (expression): The second expression.
    n (symbol): The variable with respect to which the difference delta is calculated.
    k (symbol): An additional symbol for the second expression.
    
    Returns:
    None
    
    Assertions:
    - The difference delta of e with respect to n is 2*n + 2.
    - The second-order difference delta of e2 with respect to
    """

    e = n*(n + 1)
    e2 = e * k

    assert dd(e) == 2*n + 2
    assert dd(e2, n, 2) == k*(4*n + 6)

    raises(ValueError, lambda: dd(e2))
    raises(ValueError, lambda: dd(e2, n, oo))


def test_difference_delta__Sum():
    e = Sum(1/k, (k, 1, n))
    assert dd(e, n) == 1/(n + 1)
    assert dd(e, n, 5) == Add(*[1/(i + n + 1) for i in range(5)])

    e = Sum(1/k, (k, 1, 3*n))
    assert dd(e, n) == Add(*[1/(i + 3*n + 1) for i in range(3)])

    e = n * Sum(1/k, (k, 1, n))
    assert dd(e, n) == 1 + Sum(1/k, (k, 1, n))

    e = Sum(1/k, (k, 1, n), (m, 1, n))
    assert dd(e, n) == harmonic(n)


def test_difference_delta__Add():
    """
    Tests the `dd` function for calculating the nth derivative of expressions involving sums and arithmetic operations.
    
    Parameters:
    - n (Symbol): The variable with respect to which the derivative is calculated.
    - e (Expression): The expression for which the derivative is calculated.
    
    Returns:
    - None: This function is used for testing and does not return any value. It asserts the correctness of the derivative calculation.
    
    Key Expressions:
    1. `e = n + n*(n + 1)`: Tests the derivative
    """

    e = n + n*(n + 1)
    assert dd(e, n) == 2*n + 3
    assert dd(e, n, 2) == 4*n + 8

    e = n + Sum(1/k, (k, 1, n))
    assert dd(e, n) == 1 + 1/(n + 1)
    assert dd(e, n, 5) == 5 + Add(*[1/(i + n + 1) for i in range(5)])


def test_difference_delta__Pow():
    e = 4**n
    assert dd(e, n) == 3*4**n
    assert dd(e, n, 2) == 15*4**n

    e = 4**(2*n)
    assert dd(e, n) == 15*4**(2*n)
    assert dd(e, n, 2) == 255*4**(2*n)

    e = n**4
    assert dd(e, n) == (n + 1)**4 - n**4

    e = n**n
    assert dd(e, n) == (n + 1)**(n + 1) - n**n


def test_limit_seq():
    """
    Calculate the limit of a sequence as a symbolic expression.
    
    This function computes the limit of a given sequence as a symbolic expression.
    It can handle various types of sequences, including those involving binomial coefficients, harmonic numbers, and summations.
    
    Parameters:
    e (Expression): The symbolic expression representing the sequence.
    m (Symbol, optional): An additional symbol to be used in the expression. Default is None.
    
    Returns:
    Expression: The limit of the sequence as a symbolic expression.
    
    Examples:
    """

    e = binomial(2*n, n) / Sum(binomial(2*k, k), (k, 1, n))
    assert limit_seq(e) == S(3) / 4
    assert limit_seq(e, m) == e

    e = (5*n**3 + 3*n**2 + 4) / (3*n**3 + 4*n - 5)
    assert limit_seq(e, n) == S(5) / 3

    e = (harmonic(n) * Sum(harmonic(k), (k, 1, n))) / (n * harmonic(2*n)**2)
    assert limit_seq(e, n) == 1

    e = Sum(k**2 * Sum(2**m/m, (m, 1, k)), (k, 1, n)) / (2**n*n)
    assert limit_seq(e, n) == 4

    e = (Sum(binomial(3*k, k) * binomial(5*k, k), (k, 1, n)) /
         (binomial(3*n, n) * binomial(5*n, n)))
    assert limit_seq(e, n) == S(84375) / 83351

    e = Sum(harmonic(k)**2/k, (k, 1, 2*n)) / harmonic(n)**3
    assert limit_seq(e, n) == S(1) / 3

    raises(ValueError, lambda: limit_seq(e * m))


@XFAIL
def test_limit_seq_fail():
    """
    Tests the limit sequence function with various complex summations.
    
    This function evaluates the limit of several complex summations as n approaches infinity. It checks the correctness of the limit sequence function by comparing the computed result with the expected value.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function includes several test cases with different summations and their expected limits.
    - Each test case involves nested summations and potentially complex expressions.
    - The function uses the `limit_seq` function
    """

    # improve Summation algorithm or add ad-hoc criteria
    e = (harmonic(n)**3 * Sum(1/harmonic(k), (k, 1, n)) /
         (n * Sum(harmonic(k)/k, (k, 1, n))))
    assert limit_seq(e, n) == 2

    # No unique dominant term
    e = (Sum(2**k * binomial(2*k, k) / k**2, (k, 1, n)) /
         (Sum(2**k/k*2, (k, 1, n)) * Sum(binomial(2*k, k), (k, 1, n))))
    assert limit_seq(e, n) == S(3) / 7

    # Simplifications of summations needs to be improved.
    e = n**3*Sum(2**k/k**2, (k, 1, n))**2 / (2**n * Sum(2**k/k, (k, 1, n)))
    assert limit_seq(e, n) == 2

    e = (harmonic(n) * Sum(2**k/k, (k, 1, n)) /
         (n * Sum(2**k*harmonic(k)/k**2, (k, 1, n))))
    assert limit_seq(e, n) == 1

    e = (Sum(2**k*factorial(k) / k**2, (k, 1, 2*n)) /
         (Sum(4**k/k**2, (k, 1, n)) * Sum(factorial(k), (k, 1, 2*n))))
    assert limit_seq(e, n) == S(3) / 16
