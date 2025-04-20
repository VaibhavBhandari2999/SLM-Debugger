from sympy import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Test the properties and evaluation of the reduced Planck constant (hbar).
    
    Key Parameters:
    - None
    
    Output:
    - A series of assertions checking the properties and evaluation of hbar.
    
    Properties checked:
    - is_commutative: True
    - is_real: True
    - is_positive: True
    - is_negative: False
    - is_irrational: True
    - evalf(): Returns the numerical value of hbar, approximately 1.05457162e-
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
