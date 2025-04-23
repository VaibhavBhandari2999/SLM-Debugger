from sympy import symbols, S
from sympy.parsing.ast_parser import parse_expr
from sympy.testing.pytest import raises
from sympy.core.sympify import SympifyError

def test_parse_expr():
    """
    Test the parsing of symbolic expressions.
    
    This function tests the parsing of symbolic expressions using the `parse_expr` function. It includes tests for handling incomplete expressions, converting numbers to SymPy expressions, and substituting symbols.
    
    Parameters:
    - a, b: Symbols to be used in the expression.
    
    Returns:
    - The parsed expression as a SymPy object.
    
    Raises:
    - SympifyError: If the input expression is incomplete.
    
    Examples:
    >>> a, b = symbols('a, b')
    >>> test
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
