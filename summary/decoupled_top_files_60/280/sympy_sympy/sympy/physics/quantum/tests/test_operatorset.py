from sympy import S

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

from sympy.testing.pytest import raises


def test_spin():
    """
    Test the mapping between operators and states.
    
    This function checks the mapping between operators and states for different quantum states and operators. It ensures that the correct states are returned for given operators and vice versa.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The function asserts that the correct states are returned for given operators.
    - It also checks that the correct operators are returned for given states.
    - The function tests the mapping for different quantum states and operators, including single and double operators.
    """

    assert operators_to_state({J2Op, JxOp}) == JxKet
    assert operators_to_state({J2Op, JyOp}) == JyKet
    assert operators_to_state({J2Op, JzOp}) == JzKet
    assert operators_to_state({J2Op(), JxOp()}) == JxKet
    assert operators_to_state({J2Op(), JyOp()}) == JyKet
    assert operators_to_state({J2Op(), JzOp()}) == JzKet

    assert state_to_operators(JxKet) == {J2Op, JxOp}
    assert state_to_operators(JyKet) == {J2Op, JyOp}
    assert state_to_operators(JzKet) == {J2Op, JzOp}
    assert state_to_operators(JxBra) == {J2Op, JxOp}
    assert state_to_operators(JyBra) == {J2Op, JyOp}
    assert state_to_operators(JzBra) == {J2Op, JzOp}

    assert state_to_operators(JxKet(S.Half, S.Half)) == {J2Op(), JxOp()}
    assert state_to_operators(JyKet(S.Half, S.Half)) == {J2Op(), JyOp()}
    assert state_to_operators(JzKet(S.Half, S.Half)) == {J2Op(), JzOp()}
    assert state_to_operators(JxBra(S.Half, S.Half)) == {J2Op(), JxOp()}
    assert state_to_operators(JyBra(S.Half, S.Half)) == {J2Op(), JyOp()}
    assert state_to_operators(JzBra(S.Half, S.Half)) == {J2Op(), JzOp()}


def test_op_to_state():
    assert operators_to_state(XOp) == XKet()
    assert operators_to_state(PxOp) == PxKet()
    assert operators_to_state(Operator) == Ket()

    assert state_to_operators(operators_to_state(XOp("Q"))) == XOp("Q")
    assert state_to_operators(operators_to_state(XOp())) == XOp()

    raises(NotImplementedError, lambda: operators_to_state(XKet))


def test_state_to_op():
    """
    Converts quantum states to corresponding operators and vice versa.
    
    This function handles the conversion between quantum states (Ket, Bra) and operators (Operator, XOp, PxOp). It ensures that states are converted to operators and operators are converted back to states.
    
    Parameters:
    state (Qobj): A quantum state object (Ket, Bra).
    
    Returns:
    Operator: The corresponding operator for the given state.
    
    Raises:
    NotImplementedError: If the input is an operator (XOp, PxOp
    """

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
