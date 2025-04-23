from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test if an expression contains a specific function or symbol.
    
    Parameters:
    - expr (Expression): The expression to be checked.
    - func (Symbol or Function): The function or symbol to look for in the expression.
    
    Returns:
    - bool: True if the expression contains the specified function or symbol, False otherwise.
    
    Examples:
    >>> test_has(cot(x), x)
    True
    >>> test_has(cot(x), cot)
    True
    >>> test_has(cot(x), sin)
    False
    >>> test_has(sin
    """

    assert cot(x).has(x)
    assert cot(x).has(cot)
    assert not cot(x).has(sin)
    assert sin(x).has(x)
    assert sin(x).has(sin)
    assert not sin(x).has(cot)


def test_sin_exp_rewrite():
    """
    Test the rewriting of trigonometric functions using the exponential form.
    
    This function checks the rewriting of sine and cosine functions using the exponential form. It ensures that the rewriting is reversible and that the original expression is correctly restored after multiple rewrites.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations:
    - `sin(x).rewrite(sin, exp)`: Rewrites the sine function in terms of the exponential function.
    - `sin(x).rewrite(sin, exp).rewrite(exp, sin
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
