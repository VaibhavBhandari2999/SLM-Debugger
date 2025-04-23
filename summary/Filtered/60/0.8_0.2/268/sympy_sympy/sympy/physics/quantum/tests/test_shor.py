from sympy.testing.pytest import XFAIL

from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.shor import CMod, getr


@XFAIL
def test_CMod():
    """
    Apply the CMod gate to a Qubit or Qubits.
    
    This function applies the controlled modular addition (CMod) gate to a Qubit or multiple Qubits. The CMod gate is a controlled operation that performs modular addition on the target qubit(s) based on the control qubit(s).
    
    Parameters:
    - control_qubit (int): The index of the control qubit.
    - mod_qubit (int): The index of the qubit on which the modular addition is performed.
    -
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
 getr(314, 4096, 16) == 13
