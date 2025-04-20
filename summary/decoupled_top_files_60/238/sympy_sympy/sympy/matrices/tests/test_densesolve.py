import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sympy.matrices.densesolve import LU_solve, rref_solve, cholesky_solve
from sympy import Dummy
from sympy import QQ

def test_LU_solve():
    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')

    assert LU_solve([[QQ(2), QQ(-1), QQ(-2)], [QQ(-4), QQ(6), QQ(3)], [QQ(-4), QQ(-2), QQ(8)]], [[x], [y], [z]], [[QQ(-1)], [QQ(13)], [QQ(-6)]], QQ) == [[QQ(2,1)], [QQ(3, 1)], [QQ(1, 1)]]


def test_cholesky_solve():
    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')
    assert cholesky_solve([[QQ(25), QQ(15), QQ(-5)], [QQ(15), QQ(18), QQ(0)], [QQ(-5), QQ(0), QQ(11)]], [[x], [y], [z]], [[QQ(2)], [QQ(3)], [QQ(1)]], QQ) == [[QQ(-1, 225)], [QQ(23, 135)], [QQ(4, 45)]]


def test_rref_solve():
    """
    Solve a system of linear equations using reduced row echelon form (RREF).
    
    This function takes a matrix of coefficients, a matrix of variables, and a matrix of constants, and returns the solution to the system of linear equations.
    
    Parameters:
    matrix (list of list of Rationals): The coefficient matrix of the system of equations.
    variables (list of Symbols): The list of variables in the system of equations.
    constants (list of Rationals): The constant terms of the
    """

    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')

    assert rref_solve([[QQ(25), QQ(15), QQ(-5)], [QQ(15), QQ(18), QQ(0)], [QQ(-5), QQ(0), QQ(11)]], [[x], [y], [z]], [[QQ(2)], [QQ(3)], [QQ(1)]], QQ) == [[QQ(-1, 225)], [QQ(23, 135)], [QQ(4, 45)]]
