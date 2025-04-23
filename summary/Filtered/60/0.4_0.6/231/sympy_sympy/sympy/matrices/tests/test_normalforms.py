from __future__ import print_function, division

from sympy import Symbol, Poly
from sympy.polys.solvers import RawMatrix as Matrix
from sympy.matrices.normalforms import invariant_factors, smith_normal_form
from sympy.polys.domains import ZZ, QQ

def test_smith_normal():
    """
    Tests the smith_normal_form and invariant_factors functions for a matrix with specific properties.
    
    Parameters:
    m (Matrix): The input matrix for which the smith_normal_form and invariant_factors are computed.
    ring (Ring): The ring in which the matrix operations are performed.
    
    Returns:
    tuple: A tuple containing the smith_normal_form and invariant_factors of the input matrix.
    
    Key Points:
    - The input matrix 'm' is defined with specific values and a ring attribute.
    - The smith_normal_form function returns a matrix in
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
