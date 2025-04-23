from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
    """
    Test if the given expression contains a specific symbol or function.
    
    Parameters:
    expr (Expression): The mathematical expression to be checked.
    symbol_or_function (Symbol or Function): The symbol or function to look for in the expression.
    
    Returns:
    bool: True if the expression contains the specified symbol or function, False otherwise.
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
    
    This function checks the rewriting of sine and cosine functions using the exponential form.
    It verifies that the rewritten expressions can be reverted back to the original form.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - sin(x).rewrite(sin, exp) should be equivalent to -I/2*(exp(I*x) - exp(-I*x))
    - sin(x).rewrite(sin, exp).rewrite(exp, sin) should
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
