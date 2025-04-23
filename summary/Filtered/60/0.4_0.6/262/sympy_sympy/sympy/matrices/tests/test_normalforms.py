from sympy import Symbol, Poly
from sympy.polys.solvers import RawMatrix as Matrix
from sympy.matrices.normalforms import invariant_factors, smith_normal_form
from sympy.polys.domains import ZZ, QQ

def test_smith_normal():
    """
    Compute the Smith Normal Form of a matrix and its invariant factors.
    
    This function computes the Smith Normal Form (SNF) of a given matrix and its invariant factors. The SNF of a matrix over a principal ideal domain (PID) is a diagonal matrix where the diagonal entries are the invariant factors of the matrix.
    
    Parameters:
    m (Matrix): The input matrix for which the Smith Normal Form and invariant factors are to be computed. The matrix should be defined over a principal ideal domain (PID).
    """

    m = Matrix([[12, 6, 4,8],[3,9,6,12],[2,16,14,28],[20,10,10,20]])
    setattr(m, 'ring', ZZ)
    smf = Matrix([[1, 0, 0, 0], [0, 10, 0, 0], [0, 0, -30, 0], [0, 0, 0, 0]])
    assert smith_normal_form(m) == smf

    x = Symbol('x')
    m = Matrix([[Poly(x-1), Poly(1, x),Poly(-1,x)],
                [0, Poly(x), Poly(-1,x)],
                [Poly(0,x),Poly(-1,x),Poly(x)]])
    setattr(m, 'ring', QQ[x])
    invs = (Poly(1, x), Poly(x - 1), Poly(x**2 - 1))
    assert invariant_factors(m) == invs

    m = Matrix([[2, 4]])
    setattr(m, 'ring', ZZ)
    smf = Matrix([[2, 0]])
    assert smith_normal_form(m) == smf
