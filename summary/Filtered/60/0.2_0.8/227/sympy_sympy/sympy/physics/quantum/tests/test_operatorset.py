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
    Converts quantum operators to their corresponding quantum states.
    
    This function takes a quantum operator and converts it to its corresponding quantum state. It supports specific operators like XOp and PxOp, and a generic Operator type. The function also supports converting a quantum state back to its corresponding operator.
    
    Parameters:
    - operator (XOp, PxOp, or Operator): The quantum operator to be converted.
    
    Returns:
    - XKet, PxKet, or Ket: The corresponding quantum state.
    
    Raises:
    - NotImplementedError:
    """

    assert operators_to_state(XOp) == XKet()
    assert operators_to_state(PxOp) == PxKet()
    assert operators_to_state(Operator) == Ket()

    assert state_to_operators(operators_to_state(XOp("Q"))) == XOp("Q")
    assert state_to_operators(operators_to_state(XOp())) == XOp()

    raises(NotImplementedError, lambda: operators_to_state(XKet))


def test_state_to_op():
    """
    Converts quantum state representations to corresponding operators.
    
    This function takes quantum state objects (ket or bra) and converts them into their corresponding operator representations. It also supports the conversion in the reverse direction, from operators back to states.
    
    Parameters:
    state (State): The quantum state object (ket or bra) to be converted to an operator.
    
    Returns:
    Operator: The corresponding operator representation of the input state.
    
    Raises:
    NotImplementedError: If the input is an operator instead of a state.
    
    Examples:
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
