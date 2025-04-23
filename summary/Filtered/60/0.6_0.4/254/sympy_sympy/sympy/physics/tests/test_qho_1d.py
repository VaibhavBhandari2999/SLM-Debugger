from sympy import exp, integrate, oo, Rational, pi, S, simplify, sqrt, Symbol
from sympy.core.compatibility import range
from sympy.abc import omega, m, x
from sympy.physics.qho_1d import psi_n, E_n, coherent_state
from sympy.physics.quantum.constants import hbar

nu = m * omega / hbar


def test_wavefunction():
    Psi = {
        0: (nu/pi)**(S(1)/4) * exp(-nu * x**2 /2),
        1: (nu/pi)**(S(1)/4) * sqrt(2*nu) * x * exp(-nu * x**2 /2),
        2: (nu/pi)**(S(1)/4) * (2 * nu * x**2 - 1)/sqrt(2) * exp(-nu * x**2 /2),
        3: (nu/pi)**(S(1)/4) * sqrt(nu/3) * (2 * nu * x**3 - 3 * x) * exp(-nu * x**2 /2)
    }
    for n in Psi:
        assert simplify(psi_n(n, x, m, omega) - Psi[n]) == 0


def test_norm(n=1):
    """
    Test the normalization of the wave function psi_n.
    
    This function checks the normalization of the wave function psi_n for a given range of 'n'. The wave function is normalized if the integral of its square over all space equals 1.
    
    Parameters:
    n (int): The maximum quantum number 'n' to test. Default is 1.
    
    Returns:
    None: This function does not return any value. It only asserts the normalization condition for the wave function.
    
    Example:
    >>> test_norm(
    """

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
    Test the energy levels of a quantum harmonic oscillator.
    
    This function checks the energy levels of a quantum harmonic oscillator for a given maximum quantum number `n`.
    
    Parameters:
    n (int): The maximum quantum number for which the energy levels are tested. Default is 1.
    
    Returns:
    None: This function does not return any value. It only asserts the correctness of the energy levels.
    
    Example:
    >>> test_energies(3)
    # This will test the energy levels for quantum numbers
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + Rational(1, 2))

def test_coherent_state(n=10):
    """
    Tests whether a coherent state is an eigenstate of the annihilation operator.
    
    This function checks if the coherent state |α⟩ is an eigenstate of the annihilation operator a,
    for a range of states from 0 to n. The coherent state |n⟩ is defined as the eigenstate of the
    annihilation operator with eigenvalue α, where α is a complex number.
    
    Parameters:
    n (int): The maximum quantum number n up to which the test is performed. Default is
    """

    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
