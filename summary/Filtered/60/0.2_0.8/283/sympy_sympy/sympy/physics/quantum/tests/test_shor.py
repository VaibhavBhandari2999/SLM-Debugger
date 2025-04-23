from sympy.testing.pytest import XFAIL

from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.shor import CMod, getr


@XFAIL
def test_CMod():
    assert qapply(CMod(4, 2, 2)*Qubit(0, 0, 1, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0)
    assert qapply(CMod(5, 5, 7)*Qubit(0, 0, 1, 0, 0, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
    assert qapply(CMod(3, 2, 3)*Qubit(0, 1, 0, 0, 0, 0)) == \
        Qubit(0, 1, 0, 0, 0, 1)


def test_continued_frac():
    """
    Test the continued fraction function.
    
    Args:
    numerator (int): The numerator of the fraction.
    denominator (int): The denominator of the fraction.
    max_iterations (int): The maximum number of iterations to perform.
    
    Returns:
    int: The number of iterations required to reach a certain condition in the continued fraction calculation.
    
    Raises:
    ValueError: If the denominator is zero.
    
    Example:
    >>> test_continued_frac(513, 1024, 10)
    """

    assert getr(513, 1024, 10) == 2
    assert getr(169, 1024, 11) == 6
    assert getr(314, 4096, 16) == 13
