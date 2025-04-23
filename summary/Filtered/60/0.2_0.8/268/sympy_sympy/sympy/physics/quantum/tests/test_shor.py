from sympy.testing.pytest import XFAIL

from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.shor import CMod, getr


@XFAIL
def test_CMod():
    """
    Apply the CMod gate to a quantum state.
    
    This function applies the controlled modular addition gate (CMod) to a quantum state.
    The CMod gate performs a modular addition operation on a target qubit, controlled by a control qubit, and the result is stored in the target qubit.
    
    Parameters:
    a (int): The first integer parameter for the modular addition.
    b (int): The second integer parameter for the modular addition.
    n (int): The modulus for the modular
    """

    assert qapply(CMod(4, 2, 2)*Qubit(0, 0, 1, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0)
    assert qapply(CMod(5, 5, 7)*Qubit(0, 0, 1, 0, 0, 0, 0, 0, 0, 0)) == \
        Qubit(0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
    assert qapply(CMod(3, 2, 3)*Qubit(0, 1, 0, 0, 0, 0)) == \
        Qubit(0, 1, 0, 0, 0, 1)


def test_continued_frac():
    assert getr(513, 1024, 10) == 2
    assert getr(169, 1024, 11) == 6
    assert getr(314, 4096, 16) == 13
