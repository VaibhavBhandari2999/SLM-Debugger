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
    Converts quantum operators to their corresponding state representations and vice versa.
    
    Parameters:
    - op (Operator): The quantum operator to be converted to a state.
    
    Returns:
    - State: The state representation of the given operator.
    
    Raises:
    - NotImplementedError: If the input is not an operator but a state.
    
    Examples:
    - Converting XOp to XKet: operators_to_state(XOp) == XKet()
    - Converting PxOp to PxKet: operators_to_state(PxOp) == PxK
    """

    assert operators_to_state(XOp) == XKet()
    assert operators_to_state(PxOp) == PxKet()
    assert operators_to_state(Operator) == Ket()

    assert state_to_operators(operators_to_state(XOp("Q"))) == XOp("Q")
    assert state_to_operators(operators_to_state(XOp())) == XOp()

    raises(NotImplementedError, lambda: operators_to_state(XKet))


def test_state_to_op():
    """
    Convert a quantum state to its corresponding operator representation.
    
    This function takes a quantum state (ket or bra) and converts it to its corresponding operator representation. If the state is a general ket or bra, it returns the identity operator. For specific states like X and P, it returns the corresponding Pauli operators XOp and PxOp.
    
    Parameters:
    - state: A quantum state (ket or bra) such as XKet, PxKet, XBra, PxBra, Ket, or Bra
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
