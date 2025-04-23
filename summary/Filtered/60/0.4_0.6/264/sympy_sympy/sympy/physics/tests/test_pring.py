from sympy.physics.pring import wavefunction, energy
from sympy.core.compatibility import range
from sympy import pi, integrate, sqrt, exp, simplify, I
from sympy.abc import m, x, r
from sympy.physics.quantum.constants import hbar


def test_wavefunction():
    """
    Tests the wavefunction for correctness.
    
    This function checks if the wavefunction values match the expected values for given quantum states.
    
    Parameters:
    x (Symbol): The variable representing the position or spatial coordinate.
    
    Returns:
    None: This function does not return any value. It raises an AssertionError if the wavefunction does not match the expected values.
    
    Key Parameters:
    Psi (dict): A dictionary containing the expected wavefunction values for different quantum states.
    
    Keywords:
    None
    
    Example:
    >>> test_wave
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
    
    This function checks the orthogonality of wavefunctions for a specified range of quantum numbers. It integrates the product of two wavefunctions over the interval from 0 to 2*pi and asserts that the result is zero, indicating orthogonality.
    
    Parameters:
    n (int): The maximum quantum number to test. Default is 1.
    
    Returns:
    None: The function does not return any value.
    """

    # Maximum "n" which is tested:
    for i in range(n + 1):
        for j in range(i+1, n+1):
            assert integrate(
                wavefunction(i, x) * wavefunction(j, x), (x, 0, 2 * pi)) == 0


def test_energy(n=1):
    """
    Test the energy function for correctness.
    
    This function checks if the simplified form of the energy function matches the expected mathematical expression for a given range of 'i' values.
    
    Parameters:
    n (int): The maximum value of 'i' to test. Default is 1.
    
    Returns:
    None: This function does not return any value. It only asserts the correctness of the energy function.
    
    Key Parameters:
    - i (int): The quantum number for which the energy is calculated.
    - m (float): The
    """

    # Maximum "n" which is tested:
    for i in range(n+1):
        assert simplify(
            energy(i, m, r) - ((i**2 * hbar**2) / (2 * m * r**2))) == 0
