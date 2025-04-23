from sympy.core.numbers import Float

from sympy.physics.quantum.constants import hbar


def test_hbar():
    """
    Test the properties and evaluation of the reduced Planck constant (hbar).
    
    Key properties tested:
    - Commutative nature
    - Real number status
    - Positive value
    - Non-negative value
    - Irrational number status
    
    Evaluation:
    - Numerical value in joule-seconds
    
    Parameters:
    - None
    
    Returns:
    - None
    """

    assert hbar.is_commutative is True
    assert hbar.is_real is True
    assert hbar.is_positive is True
    assert hbar.is_negative is False
    assert hbar.is_irrational is True

    assert hbar.evalf() == Float(1.05457162e-34)
