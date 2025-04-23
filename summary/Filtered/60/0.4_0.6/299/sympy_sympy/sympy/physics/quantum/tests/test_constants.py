from sympy.core.numbers import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Test the properties and evaluation of the reduced Planck constant (hbar).
    
    Key Properties:
    - is_commutative: True
    - is_real: True
    - is_positive: True
    - is_negative: False
    - is_irrational: True
    
    Evaluation:
    - evalf(): Returns the numerical value of hbar, approximately 1.05457162e-34 J*s.
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
