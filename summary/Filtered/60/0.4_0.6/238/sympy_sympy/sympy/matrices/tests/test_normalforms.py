from __future__ import print_function, division

from sympy import Symbol, Poly
from sympy.polys.solvers import RawMatrix as Matrix
from sympy.matrices.normalforms import invariant_factors, smith_normal_form
from sympy.polys.domains import ZZ, QQ

def test_smith_normal():
    """
    Compute the Smith Normal Form and Invariant Factors of a Matrix.
    
    This function computes the Smith Normal Form (SNF) and the invariant factors of a given matrix.
    
    Parameters:
    m (Matrix): The input matrix for which the Smith Normal Form and invariant factors are to be computed. The matrix should have elements from a commutative ring.
    
    Returns:
    tuple: A tuple containing two elements:
    - The Smith Normal Form (SNF) of the input matrix as a Matrix.
    -
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
