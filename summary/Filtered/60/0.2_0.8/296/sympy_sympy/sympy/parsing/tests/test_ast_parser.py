from sympy.core.singleton import S
from sympy.core.symbol import symbols
from sympy.parsing.ast_parser import parse_expr
from sympy.testing.pytest import raises
from sympy.core.sympify import SympifyError
import warnings

def test_parse_expr():
    """
    Test the parse_expr function.
    
    This function tests various aspects of the parse_expr function, including:
    - Parsing a symbolic expression with symbols 'a' and 'b'.
    - Handling incomplete expressions (e.g., 'a +').
    - Parsing constants (e.g., '1 + 2').
    - Parsing symbolic names (e.g., 'a') with a provided dictionary.
    - Handling multiplication without an explicit operator (e.g., '6 * 7').
    
    Parameters:
    - a, b: Symbols
    """

    a, b = symbols('a, b')
    # tests issue_16393
    assert parse_expr('a + b', {}) == a + b
    raises(SympifyError, lambda: parse_expr('a + ', {}))

    # tests Transform.visit_Constant
    assert parse_expr('1 + 2', {}) == S(3)
    assert parse_expr('1 + 2.0', {}) == S(3.0)

    # tests Transform.visit_Name
    assert parse_expr('Rational(1, 2)', {}) == S(1)/2
    assert parse_expr('a', {'a': a}) == a

    # tests issue_23092
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        assert parse_expr('6 * 7', {}) == S(42)
