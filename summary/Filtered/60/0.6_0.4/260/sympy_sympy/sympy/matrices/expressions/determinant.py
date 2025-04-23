from __future__ import print_function, division

from sympy import Basic, Expr, S, sympify
from .matexpr import ShapeError


class Determinant(Expr):
    """Matrix Determinant

    Represents the determinant of a matrix expression.

    Examples
    ========

    >>> from sympy import MatrixSymbol, Determinant, eye
    >>> A = MatrixSymbol('A', 3, 3)
    >>> Determinant(A)
    Determinant(A)
    >>> Determinant(eye(3)).doit()
    1
    """

    def __new__(cls, mat):
        mat = sympify(mat)
        if not mat.is_Matrix:
            raise TypeError("Input to Determinant, %s, not a matrix" % str(mat))

        if not mat.is_square:
            raise ShapeError("Det of a non-square matrix")

        return Basic.__new__(cls, mat)

    @property
    def arg(self):
        return self.args[0]

    def doit(self, expand=False):
        """
        Evaluate the determinant of the argument if possible.
        
        This method attempts to evaluate the determinant of the provided argument. If the argument supports the `_eval_determinant` method, the determinant is evaluated. Otherwise, the original argument is returned.
        
        Parameters:
        expand (bool, optional): If set to True, the method will attempt to expand the argument before evaluating the determinant. Default is False.
        
        Returns:
        The evaluated determinant of the argument if it supports the `_eval_determinant` method, otherwise
        """

        try:
            return self.arg._eval_determinant()
        except (AttributeError, NotImplementedError):
            return self

def det(matexpr):
    """ Matrix Determinant

    Examples
    ========

    >>> from sympy import MatrixSymbol, det, eye
    >>> A = MatrixSymbol('A', 3, 3)
    >>> det(A)
    Determinant(A)
    >>> det(eye(3))
    1
    """

    return Determinant(matexpr).doit()


from sympy.assumptions.ask import ask, Q
from sympy.assumptions.refine import handlers_dict


def refine_Determinant(expr, assumptions):
    """
    >>> from sympy import MatrixSymbol, Q, assuming, refine, det
    >>> X = MatrixSymbol('X', 2, 2)
    >>> det(X)
    Determinant(X)
    >>> with assuming(Q.orthogonal(X)):
    ...     print(refine(det(X)))
    1
    """
    if ask(Q.orthogonal(expr.arg), assumptions):
        return S.One
    elif ask(Q.singular(expr.arg), assumptions):
        return S.Zero
    elif ask(Q.unit_triangular(expr.arg), assumptions):
        return S.One

    return expr


handlers_dict['Determinant'] = refine_Determinant
