from sympy.physics.pring import wavefunction, energy
from sympy.core.compatibility import range
from sympy import pi, integrate, sqrt, exp, simplify, I
from sympy.abc import m, x, r
from sympy.physics.quantum.constants import hbar


def test_wavefunction():
    Psi = {
        0: (1/sqrt(2 * pi)),
        1: (1/sqrt(2 * pi)) * exp(I * x),
        2: (1/sqrt(2 * pi)) * exp(2 * I * x),
        3: (1/sqrt(2 * pi)) * exp(3 * I * x)
    }
    for n in Psi:
        assert simplify(wavefunction(n, x) - Psi[n]) == 0


def test_norm(n=1):
    """
    Test the normalization of a wavefunction.
    
    This function checks if the integral of the product of a wavefunction with its complex conjugate over the range from 0 to 2π equals 1 for all integers from 0 to n.
    
    Parameters:
    n (int): The maximum integer value to test the normalization for. Default is 1.
    
    Returns:
    None: This function does not return any value. It only asserts the correctness of the wavefunction normalization.
    
    Raises:
    AssertionError: If the integral
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert integrate(
            wavefunction(i, x) * wavefunction(-i, x), (x, 0, 2 * pi)) == 1


def test_orthogonality(n=1):
    # Maximum "n" which is tested:
    for i in range(n + 1):
        for j in range(i+1, n+1):
            assert integrate(
                wavefunction(i, x) * wavefunction(j, x), (x, 0, 2 * pi)) == 0


def test_energy(n=1):
    # Maximum "n" which is tested:
    for i in range(n+1):
        assert simplify(
            energy(i, m, r) - ((i**2 * hbar**2) / (2 * m * r**2))) == 0
