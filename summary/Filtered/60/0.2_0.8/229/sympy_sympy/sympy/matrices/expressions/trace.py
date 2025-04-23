from __future__ import print_function, division

from sympy import Basic, Expr, sympify
from sympy.matrices.matrices import MatrixBase
from .matexpr import ShapeError


class Trace(Expr):
    """Matrix Trace

    Represents the trace of a matrix expression.

    >>> from sympy import MatrixSymbol, Trace, eye
    >>> A = MatrixSymbol('A', 3, 3)
    >>> Trace(A)
    Trace(A)

    See Also:
        trace
    """
    is_Trace = True

    def __new__(cls, mat):
        """
        Create a Trace object for a given matrix.
        
        Parameters:
        - mat (sympy.Matrix): The matrix for which the trace is to be computed.
        
        Returns:
        - Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        - TypeError: If the input is not a matrix.
        - ShapeError: If the input matrix is not square.
        
        Example:
        >>> from sympy import Matrix, Trace
        >>> A = Matrix([[1, 2], [3, 4]])
        >>> Trace
        """

        mat = sympify(mat)

        if not mat.is_Matrix:
            raise TypeError("input to Trace, %s, is not a matrix" % str(mat))

        if not mat.is_square:
            raise ShapeError("Trace of a non-square matrix")

        return Basic.__new__(cls, mat)

    def _eval_transpose(self):
        return self

    @property
    def arg(self):
        return self.args[0]

    def doit(self, **kwargs):
        """
        Evaluate the trace of an expression.
        
        This function evaluates the trace of a given expression. The trace is computed based on the `deep` parameter. If `deep` is `True` (default), the function will recursively evaluate the trace of the argument. If `deep` is `False`, it will not perform a deep evaluation and will directly return the trace of the argument. If the argument is a matrix, the trace of the matrix is returned directly. Otherwise, a `Trace` object is
        """

        if kwargs.get('deep', True):
            arg = self.arg.doit(**kwargs)
            try:
                return arg._eval_trace()
            except (AttributeError, NotImplementedError):
                return Trace(arg)
        else:
            # _eval_trace would go too deep here
            if isinstance(self.arg, MatrixBase):
                return trace(self.arg)
            else:
                return Trace(self.arg)


    def _eval_rewrite_as_Sum(self):
        from sympy import Sum, Dummy
        i = Dummy('i')
        return Sum(self.arg[i, i], (i, 0, self.arg.rows-1)).doit()


def trace(expr):
    """ Trace of a Matrix.  Sum of the diagonal elements

    >>> from sympy import trace, Symbol, MatrixSymbol, pprint, eye
    >>> n = Symbol('n')
    >>> X = MatrixSymbol('X', n, n)  # A square matrix
    >>> trace(2*X)
    2*Trace(X)

    >>> trace(eye(3))
    3

    See Also:
        Trace
    """
    return Trace(expr).doit()
