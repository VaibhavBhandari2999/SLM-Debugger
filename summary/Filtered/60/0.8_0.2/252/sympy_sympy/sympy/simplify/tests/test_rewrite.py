from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test if an expression contains a specific function or symbol.
    
    This function checks if the given expression contains a specific function or symbol.
    
    Parameters:
    expr (Expr): The expression to check.
    func_or_symbol (str or Function): The function or symbol to look for in the expression.
    
    Returns:
    bool: True if the expression contains the specified function or symbol, False otherwise.
    """

    assert cot(x).has(x)
    assert cot(x).has(cot)
    assert not cot(x).has(sin)
    assert sin(x).has(x)
    assert sin(x).has(sin)
    assert not sin(x).has(cot)


def test_sin_exp_rewrite():
    """
    Test the rewriting of trigonometric functions in terms of exponential functions.
    
    This function checks the rewriting of sine and cosine functions in terms of
    exponential functions and ensures that the rewriting can be reversed.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function `sin(x).rewrite(sin, exp)` rewrites the sine function in terms of exponentials.
    - The function `cos(x).rewrite(cos, exp)` rewrites the cosine function in terms of exponentials
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
