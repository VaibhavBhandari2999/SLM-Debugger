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
    Tests the wavefunction for correctness.
    
    This function checks if the computed wavefunction matches the expected analytical form for different quantum numbers (n).
    
    Parameters:
    None (The function uses a predefined dictionary `Psi` containing the expected wavefunctions for n = 0, 1, 2, 3).
    
    Returns:
    None (The function asserts that the computed wavefunctions match the expected ones. If any assertion fails, an error will be raised).
    
    Key Points:
    - `Psi`: A dictionary
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
    None: This function does not return any value. It only asserts the correctness of the energy calculation.
    
    Notes:
    - The function uses the `E_n` function to calculate the energy levels.
    - The energy levels are expected to
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + S.Half)

def test_coherent_state(n=10):
    """
    Tests whether a coherent state is an eigenstate of the annihilation operator.
    
    This function checks if coherent states satisfy the eigenstate condition for the annihilation operator up to a given maximum number of states 'n'.
    
    Parameters:
    n (int, optional): The maximum number of coherent states to test. Default is 10.
    
    Returns:
    None: The function asserts the eigenstate condition for each tested coherent state. If any assertion fails, an error will be raised.
    
    Note:
    - The coherent state is
    """

    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
