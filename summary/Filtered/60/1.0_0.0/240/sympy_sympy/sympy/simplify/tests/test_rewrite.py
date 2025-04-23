from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test if an expression contains a specific function or symbol.
    
    Parameters:
    expr (Expression): The expression to test.
    func (Function or Symbol): The function or symbol to look for in the expression.
    
    Returns:
    bool: True if the expression contains the specified function or symbol, False otherwise.
    
    Examples:
    >>> test_has(cot(x), x)
    True
    >>> test_has(cot(x), cot)
    True
    >>> test_has(cot(x), sin)
    False
    """

    assert cot(x).has(x)
    assert cot(x).has(cot)
    assert not cot(x).has(sin)
    assert sin(x).has(x)
    assert sin(x).has(sin)
    assert not sin(x).has(cot)


def test_sin_exp_rewrite():
    """
    Test the rewriting of trigonometric functions using exponential functions.
    
    This function checks the rewriting of sine and cosine functions using the exponential form and verifies that the original form is recovered when the transformation is applied twice. It also tests the rewriting of a combination of sine and cosine functions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `sin(x).rewrite(sin, exp)`: Rewrites the sine function in terms of exponentials.
    - `sin(x).rewrite(sin,
    """

    assert sin(x).rewrite(sin, exp) == -I/2*(exp(I*x) - exp(-I*x))
    assert sin(x).rewrite(sin, exp).rewrite(exp, sin) == sin(x)
    assert cos(x).rewrite(cos, exp).rewrite(exp, cos) == cos(x)
    assert (sin(5*y) - sin(
        2*x)).rewrite(sin, exp).rewrite(exp, sin) == sin(5*y) - sin(2*x)
    assert sin(x + y).rewrite(sin, exp).rewrite(exp, sin) == sin(x + y)
    assert cos(x + y).rewrite(cos, exp).rewrite(exp, cos) == cos(x + y)
    # This next test currently passes... not clear whether it should or not?
    assert cos(x).rewrite(cos, exp).rewrite(exp, sin) == cos(x)
