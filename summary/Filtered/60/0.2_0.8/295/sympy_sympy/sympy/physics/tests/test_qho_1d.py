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
    
    This function checks if the computed wavefunction matches the expected analytical form for given quantum numbers.
    
    Parameters:
    Psi (dict): A dictionary containing the expected wavefunction values for different quantum numbers.
    
    Returns:
    None: The function asserts the correctness of the wavefunction and will raise an AssertionError if any of the values do not match.
    
    Key Parameters:
    - `Psi`: A dictionary where keys are quantum numbers (n) and values are the expected wavefunction expressions.
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
    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert E_n(i, omega) == hbar * omega * (i + S.Half)

def test_coherent_state(n=10):
    """
    Tests whether a coherent state is an eigenstate of the annihilation operator.
    
    This function checks if coherent states satisfy the eigenstate condition for the annihilation operator up to a given maximum number of states.
    
    Parameters:
    n (int): The maximum number of coherent states to test (default is 10).
    
    Returns:
    None: The function asserts the eigenstate condition for each coherent state up to the specified number.
    
    Note:
    - The coherent state is defined in terms of the parameter alpha.
    - The function
    """

    # Maximum "n" which is tested:
    # test whether coherent state is the eigenstate of annihilation operator
    alpha = Symbol("alpha")
    for i in range(n + 1):
        assert simplify(sqrt(n + 1) * coherent_state(n + 1, alpha)) == simplify(alpha * coherent_state(n, alpha))
