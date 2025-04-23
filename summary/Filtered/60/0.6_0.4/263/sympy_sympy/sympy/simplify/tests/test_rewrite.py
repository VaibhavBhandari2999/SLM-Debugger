from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test whether an expression contains a specific function or symbol.
    
    This function checks if the given expression contains a specific function or symbol.
    
    Parameters:
    expr (Expression): The expression to be checked.
    func_or_symbol (Function or Symbol): The function or symbol to look for in the expression.
    
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
    Test the rewriting of trigonometric functions (sin and cos) in terms of exponential functions (exp).
    
    Parameters:
    x, y: Symbols
    The symbols for which the trigonometric and exponential functions are evaluated.
    
    Returns:
    None
    The function asserts the correctness of the rewriting process by comparing the original and rewritten expressions.
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
