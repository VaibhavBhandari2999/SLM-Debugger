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
        
        This function initializes a Trace object, which represents the trace of a matrix. The trace of a matrix is the sum of the elements on its main diagonal.
        
        Parameters:
        mat (Matrix): A SymPy Matrix object. The input matrix must be square (i.e., it has the same number of rows and columns).
        
        Returns:
        Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        TypeError: If the input is not a
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
        """
        Evaluates the function to rewrite it as a Sum.
        
        This method transforms the function into a Sum expression. The function takes a single argument, `arg`, which is expected to be a matrix or a similar structure that can be indexed.
        
        Parameters:
        arg (Matrix or similar): The input matrix or structure to be transformed into a Sum.
        
        Returns:
        Sum: A Sum object representing the input argument with summed elements along the diagonal.
        
        Example:
        >>> from sympy import MatrixSymbol, Sum
        """

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
