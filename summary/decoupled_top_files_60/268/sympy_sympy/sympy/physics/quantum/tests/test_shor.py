from sympy.testing.pytest import XFAIL

from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.shor import CMod, getr


@XFAIL
def test_CMod():
    """
    Apply the CMod gate to a quantum state.
    
    Args:
    a (int): The modulus of the operation.
    b (int): The multiplier of the operation.
    qubits (Qubit): The quantum state to apply the operation to.
    
    Returns:
    Qubit: The resulting quantum state after applying the CMod operation.
    """

    assert qapply(CMod(4, 2, 2)*Qubit(0, 0, 1, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0)
    assert qapply(CMod(5, 5, 7)*Qubit(0, 0, 1, 0, 0, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
    assert qapply(CMod(3, 2, 3)*Qubit(0, 1, 0, 0, 0, 0)) == \
        Qubit(0, 1, 0, 0, 0, 1)


def test_continued_frac():
    """
    Calculate the number of continued fraction terms for a given numerator and denominator.
    
    Args:
    numerator (int): The numerator of the fraction.
    denominator (int): The denominator of the fraction.
    max_terms (int): The maximum number of terms to consider.
    
    Returns:
    int: The number of terms in the continued fraction representation.
    
    Raises:
    ValueError: If the denominator is zero.
    
    Examples:
    >>> test_continued_frac()
    True
    """

    assert getr(513, 1024, 10) == 2
    assert getr(169, 1024, 11) == 6
    assert getr(314, 4096, 16) == 13
