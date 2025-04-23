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
    Tests the normalization of a wavefunction for a given range of quantum numbers.
    
    This function checks the normalization of a wavefunction for a range of quantum numbers from -n to n. The wavefunction is defined by the `wavefunction` function, which should be provided as an argument. The normalization is tested by integrating the square of the wavefunction over the interval [0, 2*pi] and verifying that the result is 1.
    
    Parameters:
    n (int): The maximum quantum number to
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        assert integrate(
            wavefunction(i, x) * wavefunction(-i, x), (x, 0, 2 * pi)) == 1


def test_orthogonality(n=1):
    """
    Tests the orthogonality of wavefunctions for a given range of quantum numbers.
    
    Parameters:
    n (int): The maximum quantum number to test orthogonality for. Default is 1.
    
    This function iterates over all pairs of quantum numbers (i, j) where i and j range from 0 to n. For each pair, it checks if the integral of the product of the wavefunctions corresponding to these quantum numbers over the interval [0, 2*pi] is zero
    """

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
