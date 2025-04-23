from __future__ import print_function, division

from sympy import Basic, Expr, sympify
from sympy.matrices.matrices import MatrixBase
from .matexpr import ShapeError


class Trace(Expr):
    """Matrix Trace

    Represents the trace of a matrix expression.

    Examples
    ========

    >>> from sympy import MatrixSymbol, Trace, eye
    >>> A = MatrixSymbol('A', 3, 3)
    >>> Trace(A)
    Trace(A)
    """
    is_Trace = True

    def __new__(cls, mat):
        """
        Create a Trace object for a given matrix.
        
        Parameters:
        - mat (Matrix): A sympy matrix object. The input matrix must be square.
        
        Returns:
        - Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        - TypeError: If the input is not a matrix.
        - ShapeError: If the input matrix is not square.
        
        Example:
        >>> from sympy import Matrix
        >>> M = Matrix([[1, 2], [3, 4]])
        >>> Trace(M)
        Trace
        """

        mat = sympify(mat)

        if not mat.is_Matrix:
            raise TypeError("input to Trace, %s, is not a matrix" % str(mat))

        if not mat.is_square:
            raise ShapeError("Trace of a non-square matrix")

        return Basic.__new__(cls, mat)

    def _eval_transpose(self):
        return self

    def _eval_derivative(self, v):
        from sympy import Dummy, MatrixExpr, Sum
        if not isinstance(v, MatrixExpr):
            return None

        t1 = Dummy("t_1")
        m = Dummy("m")
        n = Dummy("n")
        # TODO: use self.rewrite(Sum) instead:
        return MatrixExpr.from_index_summation(
                Sum(self.args[0][t1, t1].diff(v[m, n]), (t1, 0, self.args[0].shape[0]-1)),
                m,
                dimensions=(v.args[1:])
            )

    @property
    def arg(self):
        return self.args[0]

    def doit(self, **kwargs):
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

    def _eval_rewrite_as_Sum(self, expr, **kwargs):
        """
        Evaluates the trace of a matrix as a Sum.
        
        This function rewrites the trace of a matrix as a Sum of its diagonal elements.
        
        Parameters:
        expr (Matrix): The matrix expression for which the trace is to be evaluated.
        
        Returns:
        Sum: The sum of the diagonal elements of the matrix.
        
        Explanation:
        The trace of a matrix is the sum of its diagonal elements. This function takes a matrix `expr` and returns the sum of its diagonal elements as a Sum object.
        """

        from sympy import Sum, Dummy
        i = Dummy('i')
        return Sum(self.arg[i, i], (i, 0, self.arg.rows-1)).doit()


def trace(expr):
    """Trace of a Matrix.  Sum of the diagonal elements.

    Examples
    ========

    >>> from sympy import trace, Symbol, MatrixSymbol, pprint, eye
    >>> n = Symbol('n')
    >>> X = MatrixSymbol('X', n, n)  # A square matrix
    >>> trace(2*X)
    2*Trace(X)
    >>> trace(eye(3))
    3
    """
    return Trace(expr).doit()
""
    return Trace(expr).doit()
