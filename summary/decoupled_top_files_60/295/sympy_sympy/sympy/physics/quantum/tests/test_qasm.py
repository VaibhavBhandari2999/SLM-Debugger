from sympy.physics.quantum.qasm import Qasm, flip_index, trim,\
     get_index, nonblank, fullsplit, fixcommand, stripquotes, read_qasm
from sympy.physics.quantum.gate import X, Z, H, S, T
from sympy.physics.quantum.gate import CNOT, SWAP, CPHASE, CGate, CGateS
from sympy.physics.quantum.circuitplot import Mz

def test_qasm_readqasm():
    """
    Reads a QASM string and returns a Quantum Circuit object.
    
    This function takes a string containing QASM (Quantum Assembly Language) instructions and converts it into a Quantum Circuit object. The QASM string should define the quantum circuit using standard QASM syntax.
    
    Parameters:
    qasm_lines (str): A string containing QASM instructions.
    
    Returns:
    QuantumCircuit: A Quantum Circuit object representing the circuit defined in the QASM string.
    
    Example:
    >>> qasm_lines = "qubit
    """

    qasm_lines = """\
    qubit q_0
    qubit q_1
    h q_0
    cnot q_0,q_1
    """
    q = read_qasm(qasm_lines)
    assert q.get_circuit() == CNOT(1,0)*H(1)

def test_qasm_ex1():
    q = Qasm('qubit q0', 'qubit q1', 'h q0', 'cnot q0,q1')
    assert q.get_circuit() == CNOT(1,0)*H(1)

def test_qasm_ex1_methodcalls():
    """
    Test QASM method calls.
    
    This function creates a Qasm object, adds qubits, applies a Hadamard gate, and a CNOT gate. It then checks if the generated circuit matches the expected CNOT(1,0)*H(1).
    
    Parameters:
    None
    
    Returns:
    None
    """

    q = Qasm()
    q.qubit('q_0')
    q.qubit('q_1')
    q.h('q_0')
    q.cnot('q_0', 'q_1')
    assert q.get_circuit() == CNOT(1,0)*H(1)

def test_qasm_swap():
    q = Qasm('qubit q0', 'qubit q1', 'cnot q0,q1', 'cnot q1,q0', 'cnot q0,q1')
    assert q.get_circuit() == CNOT(1,0)*CNOT(0,1)*CNOT(1,0)


def test_qasm_ex2():
    q = Qasm('qubit q_0', 'qubit q_1', 'qubit q_2', 'h  q_1',
             'cnot q_1,q_2', 'cnot q_0,q_1', 'h q_0',
             'measure q_1', 'measure q_0',
             'c-x q_1,q_2', 'c-z q_0,q_2')
    assert q.get_circuit() == CGate(2,Z(0))*CGate(1,X(0))*Mz(2)*Mz(1)*H(2)*CNOT(2,1)*CNOT(1,0)*H(1)

def test_qasm_1q():
    """
    Test QASM for a single qubit with various gates.
    
    This function iterates over a list of symbols representing different quantum gates and applies each gate to a single qubit. The gates include Pauli-X (x), Pauli-Z (z), Hadamard (h), S (s), T (t), and measurement (measure).
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Example:
    >>> test_qasm_1q()
    # This will generate and print the corresponding quantum circuits for
    """

    for symbol, gate in [('x', X), ('z', Z), ('h', H), ('s', S), ('t', T), ('measure', Mz)]:
        q = Qasm('qubit q_0', '%s q_0' % symbol)
        assert q.get_circuit() == gate(0)

def test_qasm_2q():
    """
    Test the Qasm function for generating a circuit with a 2-qubit gate.
    
    This function iterates over a list of gates and their corresponding symbols, creating a Qasm circuit for each gate. The circuit is then compared to the expected gate operation.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Gates and Symbols:
    - 'cnot': CNOT gate
    - 'swap': SWAP gate
    - 'cphase': CPHASE gate
    
    Each gate is applied
    """

    for symbol, gate in [('cnot', CNOT), ('swap', SWAP), ('cphase', CPHASE)]:
        q = Qasm('qubit q_0', 'qubit q_1', '%s q_0,q_1' % symbol)
        assert q.get_circuit() == gate(1,0)

def test_qasm_3q():
    q = Qasm('qubit q0', 'qubit q1', 'qubit q2', 'toffoli q2,q1,q0')
    assert q.get_circuit() == CGateS((0,1),X(2))

def test_qasm_flip_index():
    assert flip_index(0, 2) == 1
    assert flip_index(1, 2) == 0

def test_qasm_trim():
    assert trim('nothing happens here') == 'nothing happens here'
    assert trim("Something #happens here") == "Something "

def test_qasm_get_index():
    assert get_index('q0', ['q0', 'q1']) == 1
    assert get_index('q1', ['q0', 'q1']) == 0

def test_qasm_nonblank():
    assert list(nonblank('abcd')) == list('abcd')
    assert list(nonblank('abc ')) == list('abc')

def test_qasm_fullsplit():
    assert fullsplit('g q0,q1,q2,  q3') == ('g', ['q0', 'q1', 'q2', 'q3'])

def test_qasm_fixcommand():
    assert fixcommand('foo') == 'foo'
    assert fixcommand('def') == 'qdef'

def test_qasm_stripquotes():
    assert stripquotes("'S'") == 'S'
    assert stripquotes('"S"') == 'S'
    assert stripquotes('S') == 'S'

def test_qasm_qdef():
    """
    Test the Qasm class for quantum circuit definition.
    
    This function tests the Qasm class by creating quantum circuits with different definitions and qubits, and then verifying the output string representation of the circuit.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # weaker test condition (str) since we don't have access to the actual class
    q = Qasm("def Q,0,Q",'qubit q0','Q q0')
    assert str(q.get_circuit()) == 'Q(0)'

    q = Qasm("def CQ,1,Q", 'qubit q0', 'qubit q1', 'CQ q0,q1')
    assert str(q.get_circuit()) == 'C((1),Q(0))'
