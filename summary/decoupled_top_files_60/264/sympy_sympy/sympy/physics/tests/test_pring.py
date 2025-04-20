from sympy.physics.pring import wavefunction, energy
from sympy.core.compatibility import range
from sympy import pi, integrate, sqrt, exp, simplify, I
from sympy.abc import m, x, r
from sympy.physics.quantum.constants import hbar


def test_wavefunction():
    """
    Test the wavefunction for correctness.
    
    This function checks if the wavefunction values match the expected values for given quantum states.
    
    Parameters:
    Psi (dict): A dictionary where keys are quantum state indices (integers) and values are the corresponding wavefunction expressions.
    
    Returns:
    None: The function asserts that the wavefunction values match the expected values. If any value does not match, an AssertionError will be raised.
    
    Example:
    >>> Psi = {
    ...     0: (1/sqrt(2 * pi
    """

    Psi = {
        0: (1/sqrt(2 * pi)),
        1: (1/sqrt(2 * pi)) * exp(I * x),
        2: (1/sqrt(2 * pi)) * exp(2 * I * x),
        3: (1/sqrt(2 * pi)) * exp(3 * I * x)
    }
    for n in Psi:
        assert simplify(wavefunction(n, x) - Psi[n]) == 0


def test_norm(n=1):
    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert integrate(
            wavefunction(i, x) * wavefunction(-i, x), (x, 0, 2 * pi)) == 1


def test_orthogonality(n=1):
    """
    Tests the orthogonality of wavefunctions for a given range of quantum numbers.
    
    This function checks the orthogonality of wavefunctions defined by the wavefunction(i, x) and wavefunction(j, x) for all pairs (i, j) where 0 <= i <= n and i < j <= n. The orthogonality is verified by integrating the product of the two wavefunctions over the interval [0, 2*pi].
    
    Parameters:
    n (int): The
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        for j in range(i+1, n+1):
            assert integrate(
                wavefunction(i, x) * wavefunction(j, x), (x, 0, 2 * pi)) == 0


def test_energy(n=1):
    """
    Test the energy function for correctness.
    
    This function checks if the energy function returns the expected result for a given quantum number `i`. The test is performed for quantum numbers ranging from 0 to `n`.
    
    Parameters:
    n (int, optional): The maximum quantum number to test. Default is 1.
    
    Returns:
    None: The function asserts the correctness of the energy function and will raise an AssertionError if any of the tests fail.
    
    Example:
    >>> test_energy(3)
    # Tests the energy function for
    """

    # Maximum "n" which is tested:
    for i in range(n+1):
        assert simplify(
            energy(i, m, r) - ((i**2 * hbar**2) / (2 * m * r**2))) == 0
