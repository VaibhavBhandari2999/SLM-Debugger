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
        
        This function is a special method that is automatically called when a Trace object is created. It takes a matrix as input and ensures that the input is a valid matrix. If the input is not a matrix or is not square, it raises an appropriate error.
        
        Parameters:
        cls (class): The class of the Trace object being created.
        mat (Matrix): The matrix for which the Trace object is being created.
        
        Returns:
        Trace: A Trace object
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
        Evaluates the trace of a matrix as a Sum.
        
        This function rewrites the trace of a matrix as a Sum of its diagonal elements.
        
        Parameters:
        self (Matrix): The matrix whose trace is to be evaluated.
        
        Returns:
        Sum: The sum of the diagonal elements of the matrix.
        
        Explanation:
        The trace of a matrix is the sum of the elements on the main diagonal. This function computes the trace by summing the elements at positions (i, i) for all i from
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
