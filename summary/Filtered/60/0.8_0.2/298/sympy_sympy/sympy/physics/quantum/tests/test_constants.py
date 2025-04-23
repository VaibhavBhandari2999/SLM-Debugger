from sympy.core.numbers import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Test the properties and evaluation of the reduced Planck constant (hbar).
    
    This function checks the commutative, real, positive, and irrational properties of the reduced Planck constant. It also evaluates the constant to a floating-point number.
    
    Key Properties:
    - is_commutative: Whether the constant commutes with other quantities.
    - is_real: Whether the constant is a real number.
    - is_positive: Whether the constant is positive.
    - is_negative: Whether the constant is negative.
    - is
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
