from sympy import symbols, S
from sympy.parsing.ast_parser import parse_expr
from sympy.testing.pytest import raises
from sympy.core.sympify import SympifyError

def test_parse_expr():
    """
    Test the parse_expr function.
    
    This function tests the parse_expr function with various inputs and scenarios. It includes tests for handling incomplete expressions, numeric expressions, and symbol substitution.
    
    Parameters:
    - a, b: Symbols used in the test cases.
    
    Returns:
    - None: The function primarily asserts the expected behavior through assertions.
    
    Key Tests:
    1. Tests the handling of incomplete expressions, expecting a SympifyError.
    2. Tests the evaluation of numeric expressions.
    3. Tests the substitution of symbols in expressions
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
