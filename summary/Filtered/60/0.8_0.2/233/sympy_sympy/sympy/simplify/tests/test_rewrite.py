from sympy import sin, cos, exp, cot, I, symbols

x, y, z, n = symbols('x,y,z,n')


def test_has():
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
    exponential functions. It ensures that the rewriting is correctly performed
    and that the original expression can be restored by reversing the rewriting
    process.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The sine of x rewritten in terms of exponentials is equivalent to -I/2 * (exp(I*x) - exp(-I*x)).
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
