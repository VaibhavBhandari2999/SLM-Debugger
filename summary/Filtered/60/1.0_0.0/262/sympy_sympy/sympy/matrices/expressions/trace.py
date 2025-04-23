from __future__ import print_function, division

from sympy import Basic, Expr, sympify, S
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
    is_commutative = True

    def __new__(cls, mat):
        """
        Create a Trace object from a given matrix.
        
        Parameters:
        - mat (Matrix): The matrix from which to compute the trace.
        
        Returns:
        - Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        - TypeError: If the input is not a matrix.
        - ShapeError: If the input matrix is not square.
        
        Example:
        >>> from sympy import Matrix, Trace
        >>> A = Matrix([[1, 2], [3, 4]])
        >>> Trace(A)
        Trace(Matrix([
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
        from sympy import Sum
        from .matexpr import MatrixElement
        if isinstance(v, MatrixElement):
            return self.rewrite(Sum).diff(v)
        expr = self.doit()
        if isinstance(expr, Trace):
            # Avoid looping infinitely:
            raise NotImplementedError
        return expr._eval_derivative(v)

    def _eval_derivative_matrix_lines(self, x):
        """
        Evaluate the derivative matrix lines for a given expression.
        
        This function computes the derivative matrix lines for a given expression `x`.
        It processes each line in the derivative matrix and modifies it based on certain conditions.
        
        Parameters:
        x (Expr): The input expression for which the derivative matrix lines are to be evaluated.
        
        Returns:
        list: A list of modified derivative matrix lines. Each line is represented as an ExprBuilder object.
        
        Explanation:
        1. The function starts by evaluating the derivative matrix lines for
        """

        from sympy.codegen.array_utils import CodegenArrayContraction, CodegenArrayTensorProduct
        from sympy.core.expr import ExprBuilder
        r = self.args[0]._eval_derivative_matrix_lines(x)
        for lr in r:
            if lr.higher == 1:
                lr.higher = ExprBuilder(
                    CodegenArrayContraction,
                    [
                        ExprBuilder(
                            CodegenArrayTensorProduct,
                            [
                                lr._lines[0],
                                lr._lines[1],
                            ]
                        ),
                        (1, 3),
                    ],
                    validator=CodegenArrayContraction._validate
                )
            else:
                # This is not a matrix line:
                lr.higher = ExprBuilder(
                    CodegenArrayContraction,
                    [
                        ExprBuilder(
                            CodegenArrayTensorProduct,
                            [
                                lr._lines[0],
                                lr._lines[1],
                                lr.higher,
                            ]
                        ),
                        (1, 3), (0, 2)
                    ]
                )
            lr._lines = [S.One, S.One]
            lr._first_pointer_parent = lr._lines
            lr._second_pointer_parent = lr._lines
            lr._first_pointer_index = 0
            lr._second_pointer_index = 1
        return r

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
        
        This function rewrites the trace of a matrix as a Sum. The trace of a matrix
        is the sum of its diagonal elements.
        
        Parameters:
        expr (Matrix): The matrix for which the trace is to be evaluated.
        
        Returns:
        Sum: The sum of the diagonal elements of the matrix.
        
        Explanation:
        The trace of a matrix is the sum of the elements on its main diagonal.
        This function uses SymPy's `Sum
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
pr).doit()
