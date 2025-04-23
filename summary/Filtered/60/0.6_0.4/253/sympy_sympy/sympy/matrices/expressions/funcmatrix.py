from __future__ import print_function, division

from .matexpr import MatrixExpr
from sympy import Basic, sympify
from sympy.matrices import Matrix
from sympy.functions.elementary.complexes import re, im

class FunctionMatrix(MatrixExpr):
    """
    Represents a Matrix using a function (Lambda)

    This class is an alternative to SparseMatrix

    >>> from sympy import FunctionMatrix, symbols, Lambda, MatPow, Matrix
    >>> i, j = symbols('i,j')
    >>> X = FunctionMatrix(3, 3, Lambda((i, j), i + j))
    >>> Matrix(X)
    Matrix([
    [0, 1, 2],
    [1, 2, 3],
    [2, 3, 4]])

    >>> Y = FunctionMatrix(1000, 1000, Lambda((i, j), i + j))

    >>> isinstance(Y*Y, MatPow) # this is an expression object
    True

    >>> (Y**2)[10,10] # So this is evaluated lazily
    342923500
    """
    def __new__(cls, rows, cols, lamda):
        rows, cols = sympify(rows), sympify(cols)
        return Basic.__new__(cls, rows, cols, lamda)

    @property
    def shape(self):
        return self.args[0:2]

    @property
    def lamda(self):
        return self.args[2]

    def _entry(self, i, j):
        return self.lamda(i, j)

    def _eval_trace(self):
        """
        Evaluates the trace of a matrix expression.
        
        This method rewrites the trace of a matrix expression as a summation and then evaluates it.
        
        Parameters:
        None (the method operates on the instance itself)
        
        Returns:
        The evaluated trace as a summation result (sympy expression)
        
        Notes:
        - The trace of a matrix is the sum of the elements on the main diagonal.
        - The method uses SymPy's `Sum` and `Trace` classes to perform the evaluation.
        """

        from sympy.matrices.expressions.trace import Trace
        from sympy import Sum
        return Trace(self).rewrite(Sum).doit()

    def as_real_imag(self):
        return (re(Matrix(self)), im(Matrix(self)))
