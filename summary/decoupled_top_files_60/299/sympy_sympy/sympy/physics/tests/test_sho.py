from sympy.core import symbols, Rational, Function, diff
from sympy.physics.sho import R_nl, E_nl
from sympy.simplify.simplify import simplify


def test_sho_R_nl():
    """
    Tests the radial part of the Hydrogen atom wave function against the Schrodinger equation.
    
    This function checks if the radial part of the Hydrogen atom wave function, `R_nl(n, l, omega, r)`, satisfies the time-independent Schrodinger equation for a given set of quantum numbers n and l, and angular frequency omega.
    
    Parameters:
    None (The function uses symbolic variables and predefined functions)
    
    Returns:
    None (The function asserts that the radial wave function satisfies the Schrod
    """

    omega, r = symbols('omega r')
    l = symbols('l', integer=True)
    u = Function('u')

    # check that it obeys the Schrodinger equation
    for n in range(5):
        schreq = ( -diff(u(r), r, 2)/2 + ((l*(l + 1))/(2*r**2)
                    + omega**2*r**2/2 - E_nl(n, l, omega))*u(r) )
        result = schreq.subs(u(r), r*R_nl(n, l, omega/2, r))
        assert simplify(result.doit()) == 0


def test_energy():
    n, l, hw = symbols('n l hw')
    assert simplify(E_nl(n, l, hw) - (2*n + l + Rational(3, 2))*hw) == 0
