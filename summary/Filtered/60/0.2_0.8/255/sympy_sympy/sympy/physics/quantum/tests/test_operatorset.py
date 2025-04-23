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
    """
    Test the conversion between operators and states.
    
    This function checks the conversion between operators and states for the Jx, Jy, and Jz operators and their corresponding ket and bra states. It verifies that the correct operators are returned for a given state and that the correct state is returned for a given set of operators.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Operations:
    - operators_to_state: Converts a set of operators to the corresponding state.
    - state_to_operators: Converts a state
    """

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
