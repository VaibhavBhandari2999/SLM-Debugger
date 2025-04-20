from sympy.core.numbers import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Test the properties and evaluation of the reduced Planck constant (hbar).
    
    Key Parameters:
    - None
    
    Output:
    - A series of assertions checking the commutative, real, positive, and irrational properties of hbar.
    - The numerical value of hbar evaluated to a floating-point number.
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
