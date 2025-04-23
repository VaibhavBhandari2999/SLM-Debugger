from sympy.utilities.pytest import ignore_warnings
from sympy.utilities.exceptions import SymPyDeprecationWarning

with ignore_warnings(SymPyDeprecationWarning):
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
    
    This function takes a matrix of coefficients, a list of symbols representing the variables, and a list of constants as inputs. It returns the solution to the system of equations.
    
    Parameters:
    matrix (list of lists): A matrix of coefficients for the system of linear equations.
    symbols (list): A list of symbols representing the variables in the equations.
    constants (list): A list of constants on the right-hand
    """

    x, y, z = Dummy('x'), Dummy('y'), Dummy('z')

    assert rref_solve([[QQ(25), QQ(15), QQ(-5)], [QQ(15), QQ(18), QQ(0)], [QQ(-5), QQ(0), QQ(11)]], [[x], [y], [z]], [[QQ(2)], [QQ(3)], [QQ(1)]], QQ) == [[QQ(-1, 225)], [QQ(23, 135)], [QQ(4, 45)]]
