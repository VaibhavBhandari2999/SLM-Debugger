from sympy import exp, integrate, oo, Rational, pi, S, simplify, sqrt, Symbol
from sympy.core.compatibility import range
from sympy.abc import omega, m, x
from sympy.physics.qho_1d import psi_n, E_n, coherent_state
from sympy.physics.quantum.constants import hbar

nu = m * omega / hbar


def test_wavefunction():
    """
    Test the wavefunction for correctness.
    
    This function checks if the computed wavefunctions psi_n match the expected wavefunctions Psi for given quantum numbers n.
    
    Parameters:
    Psi (dict): A dictionary containing the expected wavefunctions for different quantum numbers.
    The keys are the quantum numbers (n) and the values are the corresponding wavefunctions.
    
    Returns:
    None: The function asserts that the computed wavefunctions match the expected ones. If any discrepancy is found, an assertion error will be raised.
    
    Example:
    """

    Psi = {
        0: (nu/pi)**(S(1)/4) * exp(-nu * x**2 /2),
        1: (nu/pi)**(S(1)/4) * sqrt(2*nu) * x * exp(-nu * x**2 /2),
        2: (nu/pi)**(S(1)/4) * (2 * nu * x**2 - 1)/sqrt(2) * exp(-nu * x**2 /2),
        3: (nu/pi)**(S(1)/4) * sqrt(nu/3) * (2 * nu * x**3 - 3 * x) * exp(-nu * x**2 /2)
    }
    for n in Psi:
        assert simplify(psi_n(n, x, m, omega) - Psi[n]) == 0


def test_norm(n=1):
    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert integrate(psi_n(i, x, 1, 1)**2, (x, -oo, oo)) == 1


def test_orthogonality(n=1):
    # Maximum "n" which is tested:
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            assert integrate(
                psi_n(i, x, 1, 1)*psi_n(j, x, 1, 1), (x, -oo, oo)) == 0


def test_energies(n=1):
    """
    Tests the energy levels of a quantum harmonic oscillator.
    
    This function verifies the energy levels of a quantum harmonic oscillator for a given range of quantum numbers.
    
    Parameters:
    n (int): The maximum quantum number (n) to test. Default is 1.
    
    Returns:
    None: This function does not return any value. It only asserts the correctness of the energy levels.
    
    Key Points:
    - The function uses the `assert` statement to check if the calculated energy levels match the expected values.
    - The
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + Rational(1, 2))

def test_coherent_state(n=10):
    """
    Tests whether a coherent state is an eigenstate of the annihilation operator for a given range of states.
    
    This function checks the coherent state's eigenstate property for the annihilation operator up to a specified maximum state 'n'.
    
    Parameters:
    n (int): The maximum state 'n' to test the coherent state's eigenstate property for the annihilation operator. Default is 10.
    
    Returns:
    None: The function asserts the property and does not return any value. If the assertion fails
    """

    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
