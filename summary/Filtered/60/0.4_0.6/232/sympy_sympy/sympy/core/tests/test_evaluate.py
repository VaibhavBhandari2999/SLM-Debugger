from sympy.abc import x, y
from sympy.core.evaluate import evaluate
from sympy.core import Mul, Add, Pow, S
from sympy import sqrt

def test_add():
    """
    Test addition and related operations in SymPy.
    
    This function evaluates expressions and checks the results against expected outcomes. It involves the use of the `evaluate` context manager to control the evaluation of expressions. The function tests various arithmetic operations and ensures that the results are as expected, considering the evaluation context.
    
    Key Parameters:
    - `evaluate`: A boolean value that controls whether the expressions are evaluated or not.
    
    Output:
    - The function asserts that the expressions are evaluated correctly based on the `evaluate` context. It
    """

    with evaluate(False):
        expr = x + x
        assert isinstance(expr, Add)
        assert expr.args == (x, x)

        with evaluate(True):
            assert (x + x).args == (2, x)

        assert (x + x).args == (x, x)

    assert isinstance(x + x, Mul)

    with evaluate(False):
        assert S(1) + 1 == Add(1, 1)
        assert 1 + S(1) == Add(1, 1)

        assert S(4) - 3 == Add(4, -3)
        assert -3 + S(4) == Add(4, -3)

        assert S(2) * 4 == Mul(2, 4)
        assert 4 * S(2) == Mul(2, 4)

        assert S(6) / 3 == Mul(6, S(1) / 3)
        assert S(1) / 3 * 6 == Mul(S(1) / 3, 6)

        assert 9 ** S(2) == Pow(9, 2)
        assert S(2) ** 9 == Pow(2, 9)

        assert S(2) / 2 == Mul(2, S(1) / 2)
        assert S(1) / 2 * 2 == Mul(S(1) / 2, 2)

        assert S(2) / 3 + 1 == Add(S(2) / 3, 1)
        assert 1 + S(2) / 3 == Add(1, S(2) / 3)

        assert S(4) / 7 - 3 == Add(S(4) / 7, -3)
        assert -3 + S(4) / 7 == Add(-3, S(4) / 7)

        assert S(2) / 4 * 4 == Mul(S(2) / 4, 4)
        assert 4 * (S(2) / 4) == Mul(4, S(2) / 4)

        assert S(6) / 3 == Mul(6, S(1) / 3)
        assert S(1) / 3 * 6 == Mul(S(1) / 3, 6)

        assert S(1) / 3 + sqrt(3) == Add(S(1) / 3, sqrt(3))
        assert sqrt(3) + S(1) / 3 == Add(sqrt(3), S(1) / 3)

        assert S(1) / 2 * 10.333 == Mul(S(1) / 2, 10.333)
        assert 10.333 * S(1) / 2 == Mul(10.333, S(1) / 2)

        assert sqrt(2) * sqrt(2) == Mul(sqrt(2), sqrt(2))

        assert S(1) / 2 + x == Add(S(1) / 2, x)
        assert x + S(1) / 2 == Add(x, S(1) / 2)

        assert S(1) / x * x == Mul(S(1) / x, x)
        assert x * S(1) / x == Mul(x, S(1) / x)

def test_nested():
    """
    Generate a Python docstring for the provided function.
    
    This function takes no parameters and does not return any value. It demonstrates the use of the `evaluate` context manager to modify the behavior of an expression. The expression `(x + x) + (y + y)` is simplified within the context of `evaluate(False)`, which prevents the simplification of the expression. The function asserts that the simplified expression has the correct structure, with the first argument being a tuple containing two `x` terms and
    """

    with evaluate(False):
        expr = (x + x) + (y + y)
        assert expr.args == ((x + x), (y + y))
        assert expr.args[0].args == (x, x)
