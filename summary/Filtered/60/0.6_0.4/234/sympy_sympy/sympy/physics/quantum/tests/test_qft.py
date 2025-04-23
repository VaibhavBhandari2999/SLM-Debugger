from sympy import exp, I, Matrix, pi, sqrt, Symbol

from sympy.core.compatibility import range
from sympy.physics.quantum.qft import QFT, IQFT, RkGate
from sympy.physics.quantum.gate import (ZGate, SwapGate, HadamardGate, CGate,
                                        PhaseGate, TGate)
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.represent import represent


def test_RkGate():
    x = Symbol('x')
    assert RkGate(1, x).k == x
    assert RkGate(1, x).targets == (1,)
    assert RkGate(1, 1) == ZGate(1)
    assert RkGate(2, 2) == PhaseGate(2)
    assert RkGate(3, 3) == TGate(3)

    assert represent(
        RkGate(0, x), nqubits=1) == Matrix([[1, 0], [0, exp(2*I*pi/2**x)]])


def test_quantum_fourier():
    """
    Test the Quantum Fourier Transform (QFT) and its inverse (IQFT) for a given number of qubits.
    
    This function checks the correctness of the Quantum Fourier Transform and its inverse by comparing the decomposed circuit with the expected circuit and verifying the matrix representation of the QFT. It also ensures that the QFT and IQFT operations are inverses of each other.
    
    Parameters:
    - None (The function is self-contained and uses predefined operations and assertions)
    
    Returns:
    - None (The function uses
    """

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
    Tests the equivalence of the QFT circuit and its decomposed version when represented as a matrix.
    
    This function checks if the matrix representation of a Quantum Fourier Transform (QFT) circuit and its decomposed form are the same up to a specified precision.
    
    Parameters:
    c (QuantumCircuit): The Quantum Fourier Transform circuit to test.
    
    Returns:
    None: The function asserts the equality of the matrix representations, and will raise an AssertionError if they do not match.
    
    Key Parameters:
    - `
    """

    c = QFT(0, 3)
    a = represent(c, nqubits=3)
    b = represent(c.decompose(), nqubits=3)
    assert a.evalf(prec=10) == b.evalf(prec=10)
