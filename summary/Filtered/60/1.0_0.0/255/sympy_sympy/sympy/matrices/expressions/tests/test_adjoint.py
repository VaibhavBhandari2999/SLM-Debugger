from sympy.core import symbols, S
from sympy.functions import adjoint, conjugate, transpose
from sympy.matrices.expressions import MatrixSymbol, Adjoint, trace, Transpose
from sympy.matrices import eye, Matrix

n, m, l, k, p = symbols('n m l k p', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)


def test_adjoint():
    """
    Test the adjoint (conjugate transpose) of matrices and matrix expressions.
    
    This function checks the properties and behavior of the adjoint operation on matrices and matrix expressions. It verifies the shape of the adjoint, the adjoint of the adjoint, and the interaction of the adjoint with other operations like multiplication and trace. It also tests the adjoint of specific matrix types and expressions.
    
    Parameters:
    - A, B: Matrix expressions or symbols.
    - Sq: A square matrix symbol.
    -
    """

    Sq = MatrixSymbol('Sq', n, n)

    assert Adjoint(A).shape == (m, n)
    assert Adjoint(A*B).shape == (l, n)
    assert adjoint(Adjoint(A)) == A
    assert isinstance(Adjoint(Adjoint(A)), Adjoint)

    assert conjugate(Adjoint(A)) == Transpose(A)
    assert transpose(Adjoint(A)) == Adjoint(Transpose(A))

    assert Adjoint(eye(3)).doit() == eye(3)

    assert Adjoint(S(5)).doit() == S(5)

    assert Adjoint(Matrix([[1, 2], [3, 4]])).doit() == Matrix([[1, 3], [2, 4]])

    assert adjoint(trace(Sq)) == conjugate(trace(Sq))
    assert trace(adjoint(Sq)) == conjugate(trace(Sq))

    assert Adjoint(Sq)[0, 1] == conjugate(Sq[1, 0])

    assert Adjoint(A*B).doit() == Adjoint(B) * Adjoint(A)
