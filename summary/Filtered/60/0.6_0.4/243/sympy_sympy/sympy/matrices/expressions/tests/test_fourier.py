from sympy import S, I, ask, Q, Abs, simplify, exp, sqrt
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.abc import n, i, j
def test_dft():
    """
    Test the Discrete Fourier Transform (DFT) matrix for a given size n.
    
    This function checks the properties of the DFT matrix for a given size n. It verifies the shape of the DFT matrix, checks if the matrix is unitary, confirms the determinant's absolute value is 1, and validates the inverse property of the DFT matrix.
    
    Parameters:
    n (int): The size of the DFT matrix to be tested.
    
    Returns:
    None: This function does not return any value
    """

    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)
