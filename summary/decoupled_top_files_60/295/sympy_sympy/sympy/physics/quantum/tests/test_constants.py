from sympy.core.numbers import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Tests the properties and evaluation of the reduced Planck constant (hbar).
    
    This function checks the commutative, real, positive, and irrational properties of the reduced Planck constant.
    It also evaluates the constant to a floating-point number.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - hbar.is_commutative is True
    - hbar.is_real is True
    - hbar.is_positive is True
    - hbar.is_negative is False
    - hbar.is_irrational is
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
