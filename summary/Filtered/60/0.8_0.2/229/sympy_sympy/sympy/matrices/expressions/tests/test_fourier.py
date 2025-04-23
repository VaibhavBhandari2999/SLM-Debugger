from sympy import S, I, ask, Q, Abs, simplify, exp, sqrt
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.abc import n, i, j
def test_dft():
    """
    Test the Discrete Fourier Transform (DFT) matrix for a given size `n`.
    
    This function checks the properties of the DFT matrix for a given size `n`:
    - The shape of the DFT matrix.
    - Whether the DFT matrix is unitary.
    - The determinant of the DFT matrix.
    - The property that DFT(n) * IDFT(n) should equal the identity matrix.
    - The formula for the elements of the DFT matrix.
    
    Parameters:
    n (
    """

    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)
