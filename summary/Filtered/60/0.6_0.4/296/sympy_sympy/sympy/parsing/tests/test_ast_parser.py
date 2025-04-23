from sympy.core.singleton import S
from sympy.core.symbol import symbols
from sympy.parsing.ast_parser import parse_expr
from sympy.testing.pytest import raises
from sympy.core.sympify import SympifyError
import warnings

def test_parse_expr():
    """
    Parse a string expression into a SymPy expression.
    
    This function takes a string expression and a dictionary of symbols. It returns a SymPy expression.
    Key parameters:
    - expr: The string expression to be parsed.
    - local_dict: A dictionary of symbols to be used in the expression.
    
    Returns:
    A SymPy expression.
    
    Examples:
    >>> a, b = symbols('a, b')
    >>> parse_expr('a + b', {})
    a + b
    >>> parse_expr('1 + 2', {})
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
