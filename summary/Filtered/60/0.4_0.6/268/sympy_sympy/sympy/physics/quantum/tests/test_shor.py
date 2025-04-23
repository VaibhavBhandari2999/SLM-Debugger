from sympy.testing.pytest import XFAIL

from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.shor import CMod, getr


@XFAIL
def test_CMod():
    """
    Apply the controlled modular addition operation on a quantum state.
    
    Args:
    control (int): The control qubit index.
    a (int): The first operand in the modular addition.
    b (int): The second operand in the modular addition.
    n (int): The number of qubits in the quantum state.
    
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
    assert getr(513, 1024, 10) == 2
    assert getr(169, 1024, 11) == 6
    assert getr(314, 4096, 16) == 13
