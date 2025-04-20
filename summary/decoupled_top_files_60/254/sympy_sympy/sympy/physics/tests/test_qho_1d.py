from sympy import exp, integrate, oo, Rational, pi, S, simplify, sqrt, Symbol
from sympy.core.compatibility import range
from sympy.abc import omega, m, x
from sympy.physics.qho_1d import psi_n, E_n, coherent_state
from sympy.physics.quantum.constants import hbar

nu = m * omega / hbar


def test_wavefunction():
    """
    Tests the wavefunction for correctness.
    
    This function checks if the computed wavefunctions match the expected analytical solutions for the first four energy levels of a quantum harmonic oscillator.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Variables:
    Psi (dict): A dictionary containing the analytical solutions for the wavefunctions of the first four energy levels of a quantum harmonic oscillator.
    - Keys: Integer values representing the energy level (n).
    - Values: Expressions for the wavefunction at each energy level.
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
    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + Rational(1, 2))

def test_coherent_state(n=10):
    """
    Tests whether a coherent state is an eigenstate of the annihilation operator for a given range of states.
    
    This function checks the coherent state's eigenstate property of the annihilation operator for a specified number of states.
    
    Parameters:
    n (int): The maximum number of coherent states to test (inclusive).
    
    Returns:
    None: The function asserts the property for each state in the range, raising an AssertionError if the property does not hold.
    
    Key Points:
    - The coherent state is represented by the symbol 'alpha
    """

    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
