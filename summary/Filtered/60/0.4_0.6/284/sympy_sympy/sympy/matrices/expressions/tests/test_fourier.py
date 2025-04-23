from sympy import S, I, ask, Q, Abs, simplify, exp, sqrt
from sympy.core.symbol import symbols
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.testing.pytest import raises


def test_dft_creation():
    """
    Test the creation of a Discrete Fourier Transform (DFT) object.
    
    Parameters:
    - n (int or Symbol): The number of points in the DFT or a symbolic variable representing the index.
    
    Returns:
    - DFT object: A valid DFT object if `n` is a non-negative integer.
    - ValueError: If `n` is a negative integer, a float, or a symbolic variable with non-integer or negative values.
    
    Examples:
    - DFT(2) should return a
    """

    assert DFT(2)
    assert DFT(0)
    raises(ValueError, lambda: DFT(-1))
    raises(ValueError, lambda: DFT(2.0))
    raises(ValueError, lambda: DFT(2 + 1j))

    n = symbols('n')
    assert DFT(n)
    n = symbols('n', integer=False)
    raises(ValueError, lambda: DFT(n))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: DFT(n))


def test_dft():
    n, i, j = symbols('n i j')
    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)
