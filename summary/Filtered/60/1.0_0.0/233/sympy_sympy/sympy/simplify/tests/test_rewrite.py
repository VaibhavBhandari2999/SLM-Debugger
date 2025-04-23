from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test whether an expression contains a specific symbol or function.
    
    Parameters:
    expr (Expr): The expression to test.
    symbol (Symbol or Function): The symbol or function to look for in the expression.
    
    Returns:
    bool: True if the expression contains the specified symbol or function, False otherwise.
    
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
    Test the rewriting of trigonometric functions (sin and cos) in terms of exponential functions (exp).
    
    This function checks the correctness of the rewriting of sine and cosine functions in terms of exponential functions. It also verifies the bidirectional rewriting, ensuring that the original expression is recovered after rewriting and back.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - sin(x).rewrite(sin, exp) should be equivalent to -I/2*(exp(I*x) - exp(-I*x
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
