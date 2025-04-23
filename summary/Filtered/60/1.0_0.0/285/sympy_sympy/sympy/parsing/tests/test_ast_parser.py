from sympy import symbols, S
from sympy.parsing.ast_parser import parse_expr
from sympy.testing.pytest import raises
from sympy.core.sympify import SympifyError

def test_parse_expr():
    """
    Test the parse_expr function.
    
    This function tests various aspects of the parse_expr function, including:
    - Parsing a valid expression with symbols 'a' and 'b'.
    - Handling incomplete expressions (e.g., 'a + ').
    - Parsing numeric expressions (e.g., '1 + 2').
    - Parsing symbolic expressions with custom symbol mappings (e.g., 'a' with symbol 'a').
    
    Parameters:
    - a, b: Symbols used in the test expressions.
    
    Returns:
    - The parsed
    """

    a, b = symbols('a, b')
    # tests issue_16393
    parse_expr('a + b', {}) == a + b
    raises(SympifyError, lambda: parse_expr('a + ', {}))

    # tests Transform.visit_Num
    parse_expr('1 + 2', {}) == S(3)
    parse_expr('1 + 2.0', {}) == S(3.0)

    # tests Transform.visit_Name
    parse_expr('Rational(1, 2)', {}) == S(1)/2
    parse_expr('a', {'a': a}) == a
