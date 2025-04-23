from sympy import Basic, Expr, sympify, S
from sympy.matrices.matrices import MatrixBase
from sympy.matrices.common import NonSquareMatrixError


class Trace(Expr):
    """Matrix Trace

    Represents the trace of a matrix expression.

    Examples
    ========

    >>> from sympy import MatrixSymbol, Trace, eye
    >>> A = MatrixSymbol('A', 3, 3)
    >>> Trace(A)
    Trace(A)
    >>> Trace(eye(3))
    Trace(Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]]))
    >>> Trace(eye(3)).simplify()
    3
    """
    is_Trace = True
    is_commutative = True

    def __new__(cls, mat):
        """
        Create a Trace object for a given matrix.
        
        This function is used to create a Trace object for a given matrix. The matrix must be a sympy matrix and must be square.
        
        Parameters:
        cls (class): The class of the Trace object to be created.
        mat (Matrix): The input matrix for which the trace is to be computed.
        
        Returns:
        Trace: A Trace object representing the trace of the input matrix.
        
        Raises:
        TypeError: If the input is not a sympy matrix
        """

        mat = sympify(mat)

        if not mat.is_Matrix:
            raise TypeError("input to Trace, %s, is not a matrix" % str(mat))

        if not mat.is_square:
            raise NonSquareMatrixError("Trace of a non-square matrix")

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
        Evaluates the derivative matrix lines for a given input `x`.
        
        This function processes the derivative matrix lines of a given expression with respect to `x`. It updates each line in the matrix to reflect the higher-order derivative information. The function returns a list of updated derivative matrix lines.
        
        Parameters:
        x (Symbol): The variable with respect to which the derivative is evaluated.
        
        Returns:
        list: A list of updated derivative matrix lines. Each line is represented as an ExprBuilder object.
        
        Key Steps
        """

        from sympy.tensor.array.expressions.array_expressions import ArrayTensorProduct, ArrayContraction
        from sympy.core.expr import ExprBuilder
        r = self.args[0]._eval_derivative_matrix_lines(x)
        for lr in r:
            if lr.higher == 1:
                lr.higher = ExprBuilder(
                    ArrayContraction,
                    [
                        ExprBuilder(
                            ArrayTensorProduct,
                            [
                                lr._lines[0],
                                lr._lines[1],
                            ]
                        ),
                        (1, 3),
                    ],
                    validator=ArrayContraction._validate
                )
            else:
                # This is not a matrix line:
                lr.higher = ExprBuilder(
                    ArrayContraction,
                    [
                        ExprBuilder(
                            ArrayTensorProduct,
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

    def _normalize(self):
        """
        Normalize the trace of matrix products.
        
        This function normalizes the trace of matrix products by ensuring the arguments
        of the matrix product are sorted and the first argument is not a transposition.
        
        Parameters:
        self (Trace): The Trace object to be normalized.
        
        Returns:
        Trace: A normalized Trace object with the matrix product arguments sorted
        and the first argument not being a transposition.
        
        Key Steps:
        1. Check if the argument is a MatMul (matrix product).
        2. Find the index
        """

        # Normalization of trace of matrix products. Use transposition and
        # cyclic properties of traces to make sure the arguments of the matrix
        # product are sorted and the first argument is not a trasposition.
        from sympy import MatMul, Transpose, default_sort_key
        trace_arg = self.arg
        if isinstance(trace_arg, MatMul):
            indmin = min(range(len(trace_arg.args)), key=lambda x: default_sort_key(trace_arg.args[x]))
            if isinstance(trace_arg.args[indmin], Transpose):
                trace_arg = Transpose(trace_arg).doit()
                indmin = min(range(len(trace_arg.args)), key=lambda x: default_sort_key(trace_arg.args[x]))
            trace_arg = MatMul.fromiter(trace_arg.args[indmin:] + trace_arg.args[:indmin])
            return Trace(trace_arg)
        return self

    def _eval_rewrite_as_Sum(self, expr, **kwargs):
        from sympy import Sum, Dummy
        i = Dummy('i')
        return Sum(self.arg[i, i], (i, 0, self.arg.rows-1)).doit()


def trace(expr):
    """Trace of a Matrix.  Sum of the diagonal elements.

    Examples
    ========

    >>> from sympy import trace, Symbol, MatrixSymbol, eye
    >>> n = Symbol('n')
    >>> X = MatrixSymbol('X', n, n)  # A square matrix
    >>> trace(2*X)
    2*Trace(X)
    >>> trace(eye(3))
    3
    """
    return Trace(expr).doit()
