from sympy import S, I, ask, Q, Abs, simplify, exp, sqrt
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.abc import n, i, j
def test_dft():
    """
    Test the Discrete Fourier Transform (DFT) matrix.
    
    This function checks the properties of the DFT matrix for a given size `n`.
    It verifies the shape of the DFT matrix, its unitarity, the determinant's absolute value,
    and the relationship between the DFT and IDFT matrices.
    
    Parameters:
    n (int): The size of the DFT matrix to test.
    
    Returns:
    None: This function does not return any value. It only performs assertions to check the properties of
    """

    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)
