from sympy.core.numbers import (Rational, oo, pi)
from sympy.core.singleton import S
from sympy.core.symbol import Symbol
from sympy.functions.elementary.exponential import exp
from sympy.functions.elementary.miscellaneous import sqrt
from sympy.integrals.integrals import integrate
from sympy.simplify.simplify import simplify
from sympy.abc import omega, m, x
from sympy.physics.qho_1d import psi_n, E_n, coherent_state
from sympy.physics.quantum.constants import hbar

nu = m * omega / hbar


def test_wavefunction():
    """
    Test the wavefunction for correctness.
    
    This function checks if the computed wavefunctions psi_n for different quantum numbers n match the expected analytical solutions stored in the dictionary Psi. The wavefunctions are defined in terms of the quantum number n, position x, mass m, and angular frequency omega.
    
    Parameters:
    None (the function uses a predefined dictionary Psi and symbolic variables)
    
    Returns:
    None (the function asserts the equality of the computed and expected wavefunctions)
    
    Key Variables:
    Psi (dict): A
    """

    Psi = {
        0: (nu/pi)**Rational(1, 4) * exp(-nu * x**2 /2),
        1: (nu/pi)**Rational(1, 4) * sqrt(2*nu) * x * exp(-nu * x**2 /2),
        2: (nu/pi)**Rational(1, 4) * (2 * nu * x**2 - 1)/sqrt(2) * exp(-nu * x**2 /2),
        3: (nu/pi)**Rational(1, 4) * sqrt(nu/3) * (2 * nu * x**3 - 3 * x) * exp(-nu * x**2 /2)
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
    Test the energies of a quantum harmonic oscillator.
    
    This function checks the energy levels of a quantum harmonic oscillator for a given range of quantum numbers.
    
    Parameters:
    n (int): The maximum quantum number (n) to test. Default is 1.
    
    Returns:
    None: This function does not return any value. It asserts that the calculated energy levels match the expected values.
    
    Example:
    >>> test_energies(3)
    # This will test the energy levels for quantum numbers 0 through
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + S.Half)

def test_coherent_state(n=10):
    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
herent_state(n, alpha))
