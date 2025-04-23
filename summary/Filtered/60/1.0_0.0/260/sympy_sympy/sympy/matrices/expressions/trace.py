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
        Create a Trace object for a given matrix.
        
        This function is used to create a Trace object for a given matrix. The matrix must be a square matrix, i.e., it must have the same number of rows and columns. The matrix is first converted to a SymPy matrix using `sympify`.
        
        Parameters:
        cls (class): The class of the Trace object to be created.
        mat (Matrix): The input matrix for which the Trace object is to be created.
        
        Returns:
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
        from sympy.matrices.expressions.matexpr import _matrix_derivative
        return _matrix_derivative(self, v)

    def _eval_derivative_matrix_lines(self, x):
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
        Evaluates the function to a Sum expression.
        
        This function rewrites the given expression as a Sum. It uses a dummy variable 'i' to represent the index of summation.
        
        Parameters:
        expr (sympy expression): The expression to be rewritten as a Sum.
        
        Returns:
        sympy.Sum: The Sum expression representing the original expression.
        
        Example:
        >>> from sympy import MatrixSymbol
        >>> A = MatrixSymbol('A', 3, 3)
        >>> A
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
