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
        - mat (Matrix): The matrix for which the trace is to be computed. It must be a square matrix.
        
        Returns:
        - Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        - TypeError: If the input is not a matrix.
        - ShapeError: If the input matrix is not square.
        
        Example:
        >>> from sympy import Matrix, Trace
        >>> M = Matrix([[1, 2], [3,
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
        """
        Evaluate the trace of an expression.
        
        This function evaluates the trace of a given expression. The trace is computed based on the provided arguments and keyword arguments.
        
        Parameters:
        arg (Expression): The expression for which the trace is to be evaluated.
        
        Keyword Arguments:
        deep (bool, optional): If True (default), the function will recursively evaluate the trace of the argument. If False, it will not perform a deep evaluation.
        
        Returns:
        Expression: The evaluated trace of the given expression. If deep
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

    def _eval_rewrite_as_Sum(self, expr, **kwargs):
        """
        Evaluates the function as a Sum.
        
        This method rewrites the function as a Sum expression.
        
        Parameters:
        expr (sympy expression): The expression to be rewritten as a Sum.
        
        Returns:
        sympy.Sum: The Sum expression equivalent to the input expression.
        
        Explanation:
        The function `_eval_rewrite_as_Sum` takes a sympy expression and rewrites it as a Sum. It uses a dummy variable 'i' to represent the index of summation. The Sum is created
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
