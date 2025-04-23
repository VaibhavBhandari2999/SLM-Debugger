from sympy.core.sympify import _sympify
from sympy.core import S, Basic

from sympy.matrices.common import NonSquareMatrixError
from sympy.matrices.expressions.matpow import MatPow


class Inverse(MatPow):
    """
    The multiplicative inverse of a matrix expression

    This is a symbolic object that simply stores its argument without
    evaluating it. To actually compute the inverse, use the ``.inverse()``
    method of matrices.

    Examples
    ========

    >>> from sympy import MatrixSymbol, Inverse
    >>> A = MatrixSymbol('A', 3, 3)
    >>> B = MatrixSymbol('B', 3, 3)
    >>> Inverse(A)
    A**(-1)
    >>> A.inverse() == Inverse(A)
    True
    >>> (A*B).inverse()
    B**(-1)*A**(-1)
    >>> Inverse(A*B)
    (A*B)**(-1)

    """
    is_Inverse = True
    exp = S.NegativeOne

    def __new__(cls, mat, exp=S.NegativeOne):
        # exp is there to make it consistent with
        # inverse.func(*inverse.args) == inverse
        mat = _sympify(mat)
        if not mat.is_Matrix:
            raise TypeError("mat should be a matrix")
        if not mat.is_square:
            raise NonSquareMatrixError("Inverse of non-square matrix %s" % mat)
        return Basic.__new__(cls, mat, exp)

    @property
    def arg(self):
        return self.args[0]

    @property
    def shape(self):
        return self.arg.shape

    def _eval_inverse(self):
        return self.arg

    def _eval_determinant(self):
        from sympy.matrices.expressions.determinant import det
        return 1/det(self.arg)

    def doit(self, **hints):
        """
        doit(self, **hints)
        
        Perform the inverse operation on the argument if the 'inv_expand' hint is not set to False. If the 'deep' hint is True (default), recursively apply the doit method to the argument. The function returns the inverse of the processed argument.
        
        Parameters:
        hints (dict): A dictionary of hints that can include:
        - 'inv_expand' (bool): If False, prevents the inverse operation from being applied.
        - 'deep' (bool):
        """

        if 'inv_expand' in hints and hints['inv_expand'] == False:
            return self

        arg = self.arg
        if hints.get('deep', True):
            arg = arg.doit(**hints)

        return arg.inverse()

    def _eval_derivative_matrix_lines(self, x):
        """
        Evaluates the derivative of a matrix with respect to a given variable and applies transformations to the result.
        
        This function computes the derivative of a matrix with respect to a specified variable and then applies specific transformations to each line of the resulting derivative matrix.
        
        Parameters:
        x (Symbol): The variable with respect to which the derivative is computed.
        
        Returns:
        list: A list of Line objects representing the transformed derivative matrix lines.
        
        Explanation:
        The function `_eval_derivative_matrix_lines` takes a symbolic variable `
        """

        arg = self.args[0]
        lines = arg._eval_derivative_matrix_lines(x)
        for line in lines:
            line.first_pointer *= -self.T
            line.second_pointer *= self
        return lines


from sympy.assumptions.ask import ask, Q
from sympy.assumptions.refine import handlers_dict


def refine_Inverse(expr, assumptions):
    """
    >>> from sympy import MatrixSymbol, Q, assuming, refine
    >>> X = MatrixSymbol('X', 2, 2)
    >>> X.I
    X**(-1)
    >>> with assuming(Q.orthogonal(X)):
    ...     print(refine(X.I))
    X.T
    """
    if ask(Q.orthogonal(expr), assumptions):
        return expr.arg.T
    elif ask(Q.unitary(expr), assumptions):
        return expr.arg.conjugate()
    elif ask(Q.singular(expr), assumptions):
        raise ValueError("Inverse of singular matrix %s" % expr.arg)

    return expr

handlers_dict['Inverse'] = refine_Inverse
