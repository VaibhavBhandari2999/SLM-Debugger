from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test if an expression contains a specific function or symbol.
    
    Parameters:
    expr (Expr): The expression to be checked.
    func_or_symbol (str or Function): The function or symbol to look for in the expression.
    
    Returns:
    bool: True if the expression contains the specified function or symbol, False otherwise.
    
    Examples:
    >>> test_has(cot(x), x)
    True
    >>> test_has(cot(x), cot)
    True
    >>> test_has(cot(x), sin
    """

    assert cot(x).has(x)
    assert cot(x).has(cot)
    assert not cot(x).has(sin)
    assert sin(x).has(x)
    assert sin(x).has(sin)
    assert not sin(x).has(cot)


def test_sin_exp_rewrite():
    """
    Test the rewrite functionality for trigonometric functions in terms of exponential functions.
    
    This function checks the rewrite functionality for the sine and cosine functions in SymPy, ensuring that the transformations between sine and exponential functions, and vice versa, are correctly implemented. It verifies that the transformations are reversible and that the original expressions are correctly restored after multiple rewrites.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The function tests the rewrite of sine and cosine functions using the exp function.
    - It
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
