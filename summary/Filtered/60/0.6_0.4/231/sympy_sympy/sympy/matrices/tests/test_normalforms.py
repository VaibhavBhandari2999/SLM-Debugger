from __future__ import print_function, division

from sympy import Symbol, Poly
from sympy.polys.solvers import RawMatrix as Matrix
from sympy.matrices.normalforms import invariant_factors, smith_normal_form
from sympy.polys.domains import ZZ, QQ

def test_smith_normal():
    """
    Tests the smith_normal_form and invariant_factors functions for a matrix with symbolic and integer entries.
    
    Parameters:
    m (Matrix): The input matrix for which the smith_normal_form and invariant_factors are computed.
    ring (Optional[Ring]): The ring in which the matrix entries are defined. Default is ZZ (Integer Ring).
    
    Returns:
    For smith_normal_form, returns a Matrix representing the Smith Normal Form of the input matrix.
    For invariant_factors, returns a tuple of Polynomials representing the invariant factors of the input matrix
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
