from __future__ import division, print_function

from typing import Callable

from sympy.core import Basic, Dict, Integer, S, Tuple
from sympy.core.cache import cacheit
from sympy.core.sympify import converter as sympify_converter
from sympy.matrices.dense import DenseMatrix
from sympy.matrices.expressions import MatrixExpr
from sympy.matrices.matrices import MatrixBase
from sympy.matrices.sparse import MutableSparseMatrix, SparseMatrix


def sympify_matrix(arg):
    return arg.as_immutable()
sympify_converter[MatrixBase] = sympify_matrix

class ImmutableDenseMatrix(DenseMatrix, MatrixExpr): # type: ignore
    """Create an immutable version of a matrix.

    Examples
    ========

    >>> from sympy import eye
    >>> from sympy.matrices import ImmutableMatrix
    >>> ImmutableMatrix(eye(3))
    Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]])
    >>> _[0, 0] = 42
    Traceback (most recent call last):
    ...
    TypeError: Cannot set values of ImmutableDenseMatrix
    """

    # MatrixExpr is set as NotIterable, but we want explicit matrices to be
    # iterable
    _iterable = True
    _class_priority = 8
    _op_priority = 10.001

    def __new__(cls, *args, **kwargs):
        return cls._new(*args, **kwargs)

    __hash__ = MatrixExpr.__hash__  # type: Callable[[MatrixExpr], int]

    @classmethod
    def _new(cls, *args, **kwargs):
        """
        Constructs a new ImmutableDenseMatrix instance.
        
        Parameters:
        - args: Variable length argument list. If a single argument is provided and it is an instance of ImmutableDenseMatrix, it is returned as is. Otherwise, it expects three arguments: rows (int), cols (int), and flat_list (list or Tuple).
        - kwargs: Arbitrary keyword arguments.
        - copy (bool, optional): If False, the matrix is initialized with the provided rows, cols, and flat_list without making
        """

        if len(args) == 1 and isinstance(args[0], ImmutableDenseMatrix):
            return args[0]
        if kwargs.get('copy', True) is False:
            if len(args) != 3:
                raise TypeError("'copy=False' requires a matrix be initialized as rows,cols,[list]")
            rows, cols, flat_list = args
        else:
            rows, cols, flat_list = cls._handle_creation_inputs(*args, **kwargs)
            flat_list = list(flat_list) # create a shallow copy
        rows = Integer(rows)
        cols = Integer(cols)
        if not isinstance(flat_list, Tuple):
            flat_list = Tuple(*flat_list)

        return Basic.__new__(cls, rows, cols, flat_list)

    @property
    def _mat(self):
        # self.args[2] is a Tuple.  Access to the elements
        # of a tuple are significantly faster than Tuple,
        # so return the internal tuple.
        return self.args[2].args

    def _entry(self, i, j, **kwargs):
        return DenseMatrix.__getitem__(self, (i, j))

    def __setitem__(self, *args):
        raise TypeError("Cannot set values of {}".format(self.__class__))

    def _eval_Eq(self, other):
        """Helper method for Equality with matrices.

        Relational automatically converts matrices to ImmutableDenseMatrix
        instances, so this method only applies here.  Returns True if the
        matrices are definitively the same, False if they are definitively
        different, and None if undetermined (e.g. if they contain Symbols).
        Returning None triggers default handling of Equalities.

        """
        if not hasattr(other, 'shape') or self.shape != other.shape:
            return S.false
        if isinstance(other, MatrixExpr) and not isinstance(
                other, ImmutableDenseMatrix):
            return None
        diff = (self - other).is_zero_matrix
        if diff is True:
            return S.true
        elif diff is False:
            return S.false

    def _eval_extract(self, rowsList, colsList):
        """
        Extracts a submatrix from the current matrix.
        
        Parameters:
        rowsList (list): A list of row indices to include in the submatrix.
        colsList (list): A list of column indices to include in the submatrix.
        
        Returns:
        Matrix: A new matrix containing the specified submatrix.
        
        This function takes two lists of indices, `rowsList` and `colsList`, and extracts a submatrix from the current matrix by selecting the specified rows and columns. The internal matrix
        """

        # self._mat is a Tuple.  It is slightly faster to index a
        # tuple over a Tuple, so grab the internal tuple directly
        mat = self._mat
        cols = self.cols
        indices = (i * cols + j for i in rowsList for j in colsList)
        return self._new(len(rowsList), len(colsList),
                         Tuple(*(mat[i] for i in indices), sympify=False), copy=False)

    @property
    def cols(self):
        return int(self.args[1])

    @property
    def rows(self):
        return int(self.args[0])

    @property
    def shape(self):
        return tuple(int(i) for i in self.args[:2])

    def as_immutable(self):
        return self

    def is_diagonalizable(self, reals_only=False, **kwargs):
        return super(ImmutableDenseMatrix, self).is_diagonalizable(
            reals_only=reals_only, **kwargs)
    is_diagonalizable.__doc__ = DenseMatrix.is_diagonalizable.__doc__
    is_diagonalizable = cacheit(is_diagonalizable)


# make sure ImmutableDenseMatrix is aliased as ImmutableMatrix
ImmutableMatrix = ImmutableDenseMatrix


class ImmutableSparseMatrix(SparseMatrix, Basic):
    """Create an immutable version of a sparse matrix.

    Examples
    ========

    >>> from sympy import eye
    >>> from sympy.matrices.immutable import ImmutableSparseMatrix
    >>> ImmutableSparseMatrix(1, 1, {})
    Matrix([[0]])
    >>> ImmutableSparseMatrix(eye(3))
    Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]])
    >>> _[0, 0] = 42
    Traceback (most recent call last):
    ...
    TypeError: Cannot set values of ImmutableSparseMatrix
    >>> _.shape
    (3, 3)
    """
    is_Matrix = True
    _class_priority = 9

    @classmethod
    def _new(cls, *args, **kwargs):
        """
        Create a new instance of a mutable sparse matrix.
        
        This method initializes a new mutable sparse matrix object with the given dimensions and stored matrix data. The matrix is represented using a dictionary to store non-zero elements efficiently.
        
        Parameters:
        *args: Variable length argument list. Typically used to pass the number of rows and columns, followed by the dictionary of non-zero elements.
        **kwargs: Arbitrary keyword arguments. Not used in this context but kept for compatibility.
        
        Returns:
        A new instance of the mutable
        """

        s = MutableSparseMatrix(*args)
        rows = Integer(s.rows)
        cols = Integer(s.cols)
        mat = Dict(s._smat)
        obj = Basic.__new__(cls, rows, cols, mat)
        obj.rows = s.rows
        obj.cols = s.cols
        obj._smat = s._smat
        return obj

    def __new__(cls, *args, **kwargs):
        return cls._new(*args, **kwargs)

    def __setitem__(self, *args):
        raise TypeError("Cannot set values of ImmutableSparseMatrix")

    def __hash__(self):
        return hash((type(self).__name__,) + (self.shape, tuple(self._smat)))

    _eval_Eq = ImmutableDenseMatrix._eval_Eq

    def as_immutable(self):
        return self

    def is_diagonalizable(self, reals_only=False, **kwargs):
        return super(ImmutableSparseMatrix, self).is_diagonalizable(
            reals_only=reals_only, **kwargs)
    is_diagonalizable.__doc__ = SparseMatrix.is_diagonalizable.__doc__
    is_diagonalizable = cacheit(is_diagonalizable)
