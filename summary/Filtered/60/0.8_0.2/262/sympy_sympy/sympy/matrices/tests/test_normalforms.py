from sympy import Symbol, Poly
from sympy.polys.solvers import RawMatrix as Matrix
from sympy.matrices.normalforms import invariant_factors, smith_normal_form
from sympy.polys.domains import ZZ, QQ

def test_smith_normal():
    """
    Test the Smith Normal Form and Invariant Factors of a matrix.
    
    This function tests the Smith Normal Form and Invariant Factors of a matrix
    with specified ring. It checks if the Smith Normal Form of the matrix `m` is
    equal to `smf` and if the invariant factors of the matrix `m` are equal to
    `invs`.
    
    Parameters:
    - m (Matrix): The input matrix for which the Smith Normal Form and Invariant Factors are calculated.
    - smf (Matrix
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
