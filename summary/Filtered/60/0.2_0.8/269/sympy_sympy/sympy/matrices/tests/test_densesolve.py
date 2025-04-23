from sympy.testing.pytest import ignore_warnings
from sympy.utilities.exceptions import SymPyDeprecationWarning

with ignore_warnings(SymPyDeprecationWarning):
    from sympy.matrices.densesolve import LU_solve, rref_solve, cholesky_solve

from sympy import Dummy
from sympy import QQ

def test_LU_solve():
    """
    Solve a system of linear equations using LU decomposition.
    
    This function solves the system of linear equations represented by the matrix `A` and the right-hand side vector `b` using LU decomposition.
    
    Parameters:
    A (list of list of R): The coefficient matrix of the system of linear equations.
    b (list of R): The right-hand side vector of the system of linear equations.
    b (list of R): The right-hand side vector of the system of linear equations.
    R
    """

    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')

    assert LU_solve([[QQ(2), QQ(-1), QQ(-2)], [QQ(-4), QQ(6), QQ(3)], [QQ(-4), QQ(-2), QQ(8)]], [[x], [y], [z]], [[QQ(-1)], [QQ(13)], [QQ(-6)]], QQ) == [[QQ(2,1)], [QQ(3, 1)], [QQ(1, 1)]]


def test_cholesky_solve():
    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')
    assert cholesky_solve([[QQ(25), QQ(15), QQ(-5)], [QQ(15), QQ(18), QQ(0)], [QQ(-5), QQ(0), QQ(11)]], [[x], [y], [z]], [[QQ(2)], [QQ(3)], [QQ(1)]], QQ) == [[QQ(-1, 225)], [QQ(23, 135)], [QQ(4, 45)]]


def test_rref_solve():
    """
    Solve a system of linear equations using Reduced Row Echelon Form (RREF).
    
    This function takes a matrix of coefficients, a matrix of variables, and a matrix of constants, and returns the solution to the system of linear equations.
    
    Parameters:
    matrix (list of list of Rational): The coefficient matrix of the system of equations.
    variables (list of Symbol): The variables in the system of equations.
    constants (list of Rational): The constant terms on the right-hand side of the
    """

    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')

    assert rref_solve([[QQ(25), QQ(15), QQ(-5)], [QQ(15), QQ(18), QQ(0)], [QQ(-5), QQ(0), QQ(11)]], [[x], [y], [z]], [[QQ(2)], [QQ(3)], [QQ(1)]], QQ) == [[QQ(-1, 225)], [QQ(23, 135)], [QQ(4, 45)]]
