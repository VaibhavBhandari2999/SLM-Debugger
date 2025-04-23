from __future__ import print_function, division

from sympy.matrices.expressions import MatrixExpr
from sympy.core import S, Eq
from sympy.functions.special.tensor_functions import KroneckerDelta
class DiagonalMatrix(MatrixExpr):
    arg = property(lambda self: self.args[0])
    shape = property(lambda self: (self.arg.shape[0], self.arg.shape[0]))

    def _entry(self, i, j):
        """
        Generate the entry of the diagonal matrix.
        
        This function returns the diagonal entry of the matrix at position (i, j).
        
        Parameters
        ----------
        i : int
        The row index of the matrix.
        j : int
        The column index of the matrix.
        
        Returns
        -------
        output : Expr
        The value of the matrix entry at position (i, j). It returns the diagonal
        element if i equals j, zero if i does not equal j, and the specified
        diagonal element if
        """

        eq = Eq(i, j)
        if eq is S.false:
            return S.Zero
        elif eq is S.true:
            return self.arg[i, i]
        return self.arg[i, j]*KroneckerDelta(i, j)

class DiagonalOf(MatrixExpr):
    arg = property(lambda self: self.args[0])
    shape = property(lambda self: (self.arg.shape[0], S.One))

    def _entry(self, i, j):
        return self.arg[i, i]
