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
    - Parsing a symbolic expression with multiple symbols.
    - Handling incomplete expressions.
    - Parsing constants.
    - Parsing symbolic names with provided mappings.
    - Handling multiplication without explicit operators.
    
    Parameters:
    - a, b: Symbols representing variables in the expressions.
    
    Returns:
    - The parsed expression as a SymPy object.
    
    Raises:
    - SympifyError: If the expression is incomplete.
    - Warning: If there are issues with
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
