from sympy import exp, I, Matrix, pi, sqrt, Symbol

from sympy.core.compatibility import range
from sympy.physics.quantum.qft import QFT, IQFT, RkGate
from sympy.physics.quantum.gate import (ZGate, SwapGate, HadamardGate, CGate,
                                        PhaseGate, TGate)
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.represent import represent


def test_RkGate():
    """
    Tests the RkGate function.
    
    This function checks the behavior of the RkGate function for different inputs. It verifies that the gate's k parameter is set correctly, its target qubit is identified, and that it correctly simplifies to known gates for specific values of k. It also tests the representation of the gate for a single qubit.
    
    Parameters:
    - x (Symbol): The k parameter of the RkGate.
    
    Returns:
    - None: This function does not return any value. It
    """

    x = Symbol('x')
    assert RkGate(1, x).k == x
    assert RkGate(1, x).targets == (1,)
    assert RkGate(1, 1) == ZGate(1)
    assert RkGate(2, 2) == PhaseGate(2)
    assert RkGate(3, 3) == TGate(3)

    assert represent(
        RkGate(0, x), nqubits=1) == Matrix([[1, 0], [0, exp(2*I*pi/2**x)]])


def test_quantum_fourier():
    assert QFT(0, 3).decompose() == \
        SwapGate(0, 2)*HadamardGate(0)*CGate((0,), PhaseGate(1)) * \
        HadamardGate(1)*CGate((0,), TGate(2))*CGate((1,), PhaseGate(2)) * \
        HadamardGate(2)

    assert IQFT(0, 3).decompose() == \
        HadamardGate(2)*CGate((1,), RkGate(2, -2))*CGate((0,), RkGate(2, -3)) * \
        HadamardGate(1)*CGate((0,), RkGate(1, -2))*HadamardGate(0)*SwapGate(0, 2)

    assert represent(QFT(0, 3), nqubits=3) == \
        Matrix([[exp(2*pi*I/8)**(i*j % 8)/sqrt(8) for i in range(8)] for j in range(8)])

    assert QFT(0, 4).decompose()  # non-trivial decomposition
    assert qapply(QFT(0, 3).decompose()*Qubit(0, 0, 0)).expand() == qapply(
        HadamardGate(0)*HadamardGate(1)*HadamardGate(2)*Qubit(0, 0, 0)
    ).expand()


def test_qft_represent():
    """
    Tests the equivalence of the QFT (Quantum Fourier Transform) circuit and its decomposed version when represented as a matrix.
    
    Parameters:
    c (QuantumCircuit): The Quantum Fourier Transform circuit to be tested.
    
    Returns:
    None: The function asserts that the matrix representations of the original and decomposed QFT circuits are equal up to a precision of 10 decimal places.
    
    Notes:
    - The function uses the `represent` method to obtain the matrix representation of the circuits.
    """

    c = QFT(0, 3)
    a = represent(c, nqubits=3)
    b = represent(c.decompose(), nqubits=3)
    assert a.evalf(prec=10) == b.evalf(prec=10)
