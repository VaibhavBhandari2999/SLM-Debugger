from sympy.physics.quantum.operatorset import (
    operators_to_state, state_to_operators
)

from sympy.physics.quantum.cartesian import (
    XOp, XKet, PxOp, PxKet, XBra, PxBra
)

from sympy.physics.quantum.state import Ket, Bra
from sympy.physics.quantum.operator import Operator
from sympy.physics.quantum.spin import (
    JxKet, JyKet, JzKet, JxBra, JyBra, JzBra,
    JxOp, JyOp, JzOp, J2Op
)

from sympy.utilities.pytest import raises

from sympy.utilities.pytest import XFAIL


@XFAIL
def test_spin():
    assert operators_to_state({J2Op, JxOp}) == JxKet()
    assert operators_to_state({J2Op, JyOp}) == JyKet()
    assert operators_to_state({J2Op, JzOp}) == JzKet()
    assert operators_to_state({J2Op(), JxOp()}) == JxKet()
    assert operators_to_state({J2Op(), JyOp()}) == JyKet()
    assert operators_to_state({J2Op(), JzOp()}) == JzKet()

    assert state_to_operators(JxKet) == {J2Op(), JxOp()}
    assert state_to_operators(JyKet) == {J2Op(), JyOp()}
    assert state_to_operators(JzKet) == {J2Op(), JzOp()}
    assert state_to_operators(JxBra) == {J2Op(), JxOp()}
    assert state_to_operators(JyBra) == {J2Op(), JyOp()}
    assert state_to_operators(JzBra) == {J2Op(), JzOp()}

    assert state_to_operators(JxKet()) == {J2Op(), JxOp()}
    assert state_to_operators(JyKet()) == {J2Op(), JyOp()}
    assert state_to_operators(JzKet()) == {J2Op(), JzOp()}
    assert state_to_operators(JxBra()) == {J2Op(), JxOp()}
    assert state_to_operators(JyBra()) == {J2Op(), JyOp()}
    assert state_to_operators(JzBra()) == {J2Op(), JzOp()}


def test_op_to_state():
    """
    Converts quantum operators to their corresponding state representations.
    
    Parameters:
    - XOp (Operator): X operator.
    - PxOp (Operator): Momentum X operator.
    - Operator (Operator): General quantum operator.
    
    Returns:
    - XKet (Ket): State representation of X operator.
    - PxKet (Ket): State representation of Momentum X operator.
    - Ket (Ket): State representation of a general quantum operator.
    
    Raises:
    - NotImplementedError: If the input is a Ket object instead of an Operator
    """

    assert operators_to_state(XOp) == XKet()
    assert operators_to_state(PxOp) == PxKet()
    assert operators_to_state(Operator) == Ket()

    assert state_to_operators(operators_to_state(XOp("Q"))) == XOp("Q")
    assert state_to_operators(operators_to_state(XOp())) == XOp()

    raises(NotImplementedError, lambda: operators_to_state(XKet))


def test_state_to_op():
    assert state_to_operators(XKet) == XOp()
    assert state_to_operators(PxKet) == PxOp()
    assert state_to_operators(XBra) == XOp()
    assert state_to_operators(PxBra) == PxOp()
    assert state_to_operators(Ket) == Operator()
    assert state_to_operators(Bra) == Operator()

    assert operators_to_state(state_to_operators(XKet("test"))) == XKet("test")
    assert operators_to_state(state_to_operators(XBra("test"))) == XKet("test")
    assert operators_to_state(state_to_operators(XKet())) == XKet()
    assert operators_to_state(state_to_operators(XBra())) == XKet()

    raises(NotImplementedError, lambda: state_to_operators(XOp))
