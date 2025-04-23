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
    Test the rewriting of trigonometric functions (sin and cos) in terms of exponential functions (exp).
    
    This function checks the correctness of the rewriting of sine and cosine functions in terms of exponential functions and vice versa. It verifies that the original expressions can be correctly transformed and then back-transformed to their original form.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function tests the rewriting of `sin(x)` and `cos(x)` using the `exp` function.
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
