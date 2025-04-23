from sympy import S, I, ask, Q, Abs, simplify, exp, sqrt
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.abc import n, i, j
def test_dft():
    """
    Test the Discrete Fourier Transform (DFT) matrix for a given size n.
    
    This function checks the properties of the DFT matrix for a given size n.
    It verifies the shape of the DFT matrix, its unitarity, the determinant's absolute value,
    the correctness of the DFT and IDFT multiplication, and the formula of the DFT elements.
    
    Parameters:
    n (int): The size of the DFT matrix.
    
    Returns:
    None: This function does not return any value
    """

    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)
