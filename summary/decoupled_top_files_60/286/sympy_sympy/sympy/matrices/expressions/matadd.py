from functools import reduce
import operator

from sympy.core import Add, Basic, sympify
from sympy.core.add import add
from sympy.functions import adjoint
from sympy.matrices.common import ShapeError
from sympy.matrices.matrices import MatrixBase
from sympy.matrices.expressions.transpose import transpose
from sympy.strategies import (rm_id, unpack, flatten, sort, condition,
    exhaust, do_one, glom)
from sympy.matrices.expressions.matexpr import MatrixExpr
from sympy.matrices.expressions.special import ZeroMatrix, GenericZeroMatrix
from sympy.utilities import default_sort_key, sift

# XXX: MatAdd should perhaps not subclass directly from Add
class MatAdd(MatrixExpr, Add):
    """A Sum of Matrix Expressions

    MatAdd inherits from and operates like SymPy Add

    Examples
    ========

    >>> from sympy import MatAdd, MatrixSymbol
    >>> A = MatrixSymbol('A', 5, 5)
    >>> B = MatrixSymbol('B', 5, 5)
    >>> C = MatrixSymbol('C', 5, 5)
    >>> MatAdd(A, B, C)
    A + B + C
    """
    is_MatAdd = True

    identity = GenericZeroMatrix()

    def __new__(cls, *args, evaluate=False, check=False, _sympify=True):
        """
        Constructs a new matrix expression.
        
        This function is the constructor for matrix expressions. It takes the following parameters:
        
        - `*args`: The arguments to initialize the matrix expression. These can be any valid matrix expressions or scalar values.
        - `evaluate` (bool, optional): If True, the matrix expression is evaluated immediately. Default is False.
        - `check` (bool, optional): If True, the input arguments are checked for validity. Default is False.
        - `_sympify` (
        """

        if not args:
            return cls.identity

        # This must be removed aggressively in the constructor to avoid
        # TypeErrors from GenericZeroMatrix().shape
        args = list(filter(lambda i: cls.identity != i, args))
        if _sympify:
            args = list(map(sympify, args))

        obj = Basic.__new__(cls, *args)

        if check:
            if all(not isinstance(i, MatrixExpr) for i in args):
                return Add.fromiter(args)
            validate(*args)

        if evaluate:
            if all(not isinstance(i, MatrixExpr) for i in args):
                return Add(*args, evaluate=True)
            obj = canonicalize(obj)

        return obj

    @property
    def shape(self):
        return self.args[0].shape

    def _entry(self, i, j, **kwargs):
        return Add(*[arg._entry(i, j, **kwargs) for arg in self.args])

    def _eval_transpose(self):
        return MatAdd(*[transpose(arg) for arg in self.args]).doit()

    def _eval_adjoint(self):
        return MatAdd(*[adjoint(arg) for arg in self.args]).doit()

    def _eval_trace(self):
        from .trace import trace
        return Add(*[trace(arg) for arg in self.args]).doit()

    def doit(self, **kwargs):
        deep = kwargs.get('deep', True)
        if deep:
            args = [arg.doit(**kwargs) for arg in self.args]
        else:
            args = self.args
        return canonicalize(MatAdd(*args))

    def _eval_derivative_matrix_lines(self, x):
        add_lines = [arg._eval_derivative_matrix_lines(x) for arg in self.args]
        return [j for i in add_lines for j in i]

add.register_handlerclass((Add, MatAdd), MatAdd)

def validate(*args):
    """
    Validate that multiple matrices are of the same type and shape.
    
    This function checks if all provided arguments are instances of the Matrix class and if they have the same shape.
    
    Parameters:
    *args: Variable length argument list of objects to be validated.
    
    Raises:
    TypeError: If any argument is not an instance of the Matrix class.
    ShapeError: If any two matrices do not have the same shape.
    
    Example:
    >>> validate(matrix1, matrix2)
    # No exception if matrix1 and
    """

    if not all(arg.is_Matrix for arg in args):
        raise TypeError("Mix of Matrix and Scalar symbols")

    A = args[0]
    for B in args[1:]:
        if A.shape != B.shape:
            raise ShapeError("Matrices %s and %s are not aligned"%(A, B))

factor_of = lambda arg: arg.as_coeff_mmul()[0]
matrix_of = lambda arg: unpack(arg.as_coeff_mmul()[1])
def combine(cnt, mat):
    if cnt == 1:
        return mat
    else:
        return cnt * mat


def merge_explicit(matadd):
    """ Merge explicit MatrixBase arguments

    Examples
    ========

    >>> from sympy import MatrixSymbol, eye, Matrix, MatAdd, pprint
    >>> from sympy.matrices.expressions.matadd import merge_explicit
    >>> A = MatrixSymbol('A', 2, 2)
    >>> B = eye(2)
    >>> C = Matrix([[1, 2], [3, 4]])
    >>> X = MatAdd(A, B, C)
    >>> pprint(X)
        [1  0]   [1  2]
    A + [    ] + [    ]
        [0  1]   [3  4]
    >>> pprint(merge_explicit(X))
        [2  2]
    A + [    ]
        [3  5]
    """
    groups = sift(matadd.args, lambda arg: isinstance(arg, MatrixBase))
    if len(groups[True]) > 1:
        return MatAdd(*(groups[False] + [reduce(operator.add, groups[True])]))
    else:
        return matadd


rules = (rm_id(lambda x: x == 0 or isinstance(x, ZeroMatrix)),
         unpack,
         flatten,
         glom(matrix_of, factor_of, combine),
         merge_explicit,
         sort(default_sort_key))

canonicalize = exhaust(condition(lambda x: isinstance(x, MatAdd),
                                 do_one(*rules)))
                      do_one(*rules)))
