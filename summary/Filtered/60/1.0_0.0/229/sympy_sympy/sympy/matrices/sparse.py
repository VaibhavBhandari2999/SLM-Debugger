from __future__ import print_function, division

import copy
from collections import defaultdict

from sympy.core.containers import Dict
from sympy.core.expr import Expr
from sympy.core.compatibility import is_sequence, as_int, range
from sympy.core.logic import fuzzy_and
from sympy.core.singleton import S
from sympy.functions.elementary.miscellaneous import sqrt
from sympy.utilities.iterables import uniq

from .matrices import MatrixBase, ShapeError, a2idx
from .dense import Matrix
import collections


class SparseMatrix(MatrixBase):
    """
    A sparse matrix (a matrix with a large number of zero elements).

    Examples
    ========

    >>> from sympy.matrices import SparseMatrix
    >>> SparseMatrix(2, 2, range(4))
    Matrix([
    [0, 1],
    [2, 3]])
    >>> SparseMatrix(2, 2, {(1, 1): 2})
    Matrix([
    [0, 0],
    [0, 2]])

    See Also
    ========
    sympy.matrices.dense.Matrix
    """

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        if len(args) == 1 and isinstance(args[0], SparseMatrix):
            self.rows = args[0].rows
            self.cols = args[0].cols
            self._smat = dict(args[0]._smat)
            return self

        self._smat = {}

        if len(args) == 3:
            self.rows = as_int(args[0])
            self.cols = as_int(args[1])

            if isinstance(args[2], collections.Callable):
                op = args[2]
                for i in range(self.rows):
                    for j in range(self.cols):
                        value = self._sympify(
                            op(self._sympify(i), self._sympify(j)))
                        if value:
                            self._smat[(i, j)] = value
            elif isinstance(args[2], (dict, Dict)):
                # manual copy, copy.deepcopy() doesn't work
                for key in args[2].keys():
                    v = args[2][key]
                    if v:
                        self._smat[key] = self._sympify(v)
            elif is_sequence(args[2]):
                if len(args[2]) != self.rows*self.cols:
                    raise ValueError(
                        'List length (%s) != rows*columns (%s)' %
                        (len(args[2]), self.rows*self.cols))
                flat_list = args[2]
                for i in range(self.rows):
                    for j in range(self.cols):
                        value = self._sympify(flat_list[i*self.cols + j])
                        if value:
                            self._smat[(i, j)] = value
        else:
            # handle full matrix forms with _handle_creation_inputs
            r, c, _list = Matrix._handle_creation_inputs(*args)
            self.rows = r
            self.cols = c
            for i in range(self.rows):
                for j in range(self.cols):
                    value = _list[self.cols*i + j]
                    if value:
                        self._smat[(i, j)] = value
        return self

    def __eq__(self, other):
        try:
            if self.shape != other.shape:
                return False
            if isinstance(other, SparseMatrix):
                return self._smat == other._smat
            elif isinstance(other, MatrixBase):
                return self._smat == MutableSparseMatrix(other)._smat
        except AttributeError:
            return False

    def __getitem__(self, key):
        """
        Retrieve an element or submatrix from the matrix.
        
        Parameters:
        key (tuple, slice, or int): The key used to index the matrix.
        - If a tuple (i, j) is provided, it is treated as a specific element (i, j) in the matrix.
        - If a slice is provided, it is used to extract a submatrix.
        - If an integer is provided, it is treated as a single element in the matrix.
        
        Returns:
        -
        """


        if isinstance(key, tuple):
            i, j = key
            try:
                i, j = self.key2ij(key)
                return self._smat.get((i, j), S.Zero)
            except (TypeError, IndexError):
                if isinstance(i, slice):
                    # XXX remove list() when PY2 support is dropped
                    i = list(range(self.rows))[i]
                elif is_sequence(i):
                    pass
                elif isinstance(i, Expr) and not i.is_number:
                    from sympy.matrices.expressions.matexpr import MatrixElement
                    return MatrixElement(self, i, j)
                else:
                    if i >= self.rows:
                        raise IndexError('Row index out of bounds')
                    i = [i]
                if isinstance(j, slice):
                    # XXX remove list() when PY2 support is dropped
                    j = list(range(self.cols))[j]
                elif is_sequence(j):
                    pass
                elif isinstance(j, Expr) and not j.is_number:
                    from sympy.matrices.expressions.matexpr import MatrixElement
                    return MatrixElement(self, i, j)
                else:
                    if j >= self.cols:
                        raise IndexError('Col index out of bounds')
                    j = [j]
                return self.extract(i, j)

        # check for single arg, like M[:] or M[3]
        if isinstance(key, slice):
            lo, hi = key.indices(len(self))[:2]
            L = []
            for i in range(lo, hi):
                m, n = divmod(i, self.cols)
                L.append(self._smat.get((m, n), S.Zero))
            return L

        i, j = divmod(a2idx(key, len(self)), self.cols)
        return self._smat.get((i, j), S.Zero)

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def _cholesky_solve(self, rhs):
        # for speed reasons, this is not uncommented, but if you are
        # having difficulties, try uncommenting to make sure that the
        # input matrix is symmetric

        #assert self.is_symmetric()
        L = self._cholesky_sparse()
        Y = L._lower_triangular_solve(rhs)
        rv = L.T._upper_triangular_solve(Y)
        return rv

    def _cholesky_sparse(self):
        """Algorithm for numeric Cholesky factorization of a sparse matrix."""
        Crowstruc = self.row_structure_symbolic_cholesky()
        C = self.zeros(self.rows)
        for i in range(len(Crowstruc)):
            for j in Crowstruc[i]:
                if i != j:
                    C[i, j] = self[i, j]
                    summ = 0
                    for p1 in Crowstruc[i]:
                        if p1 < j:
                            for p2 in Crowstruc[j]:
                                if p2 < j:
                                    if p1 == p2:
                                        summ += C[i, p1]*C[j, p1]
                                else:
                                    break
                            else:
                                break
                    C[i, j] -= summ
                    C[i, j] /= C[j, j]
                else:
                    C[j, j] = self[j, j]
                    summ = 0
                    for k in Crowstruc[j]:
                        if k < j:
                            summ += C[j, k]**2
                        else:
                            break
                    C[j, j] -= summ
                    C[j, j] = sqrt(C[j, j])

        return C

    def _diagonal_solve(self, rhs):
        "Diagonal solve."
        return self._new(self.rows, 1, lambda i, j: rhs[i, 0] / self[i, i])

    def _eval_inverse(self, **kwargs):
        """Return the matrix inverse using Cholesky or LDL (default)
        decomposition as selected with the ``method`` keyword: 'CH' or 'LDL',
        respectively.

        Examples
        ========

        >>> from sympy import SparseMatrix, Matrix
        >>> A = SparseMatrix([
        ... [ 2, -1,  0],
        ... [-1,  2, -1],
        ... [ 0,  0,  2]])
        >>> A.inv('CH')
        Matrix([
        [2/3, 1/3, 1/6],
        [1/3, 2/3, 1/3],
        [  0,   0, 1/2]])
        >>> A.inv(method='LDL') # use of 'method=' is optional
        Matrix([
        [2/3, 1/3, 1/6],
        [1/3, 2/3, 1/3],
        [  0,   0, 1/2]])
        >>> A * _
        Matrix([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]])

        """
        sym = self.is_symmetric()
        M = self.as_mutable()
        I = M.eye(M.rows)
        if not sym:
            t = M.T
            r1 = M[0, :]
            M = t*M
            I = t*I
        method = kwargs.get('method', 'LDL')
        if method in "LDL":
            solve = M._LDL_solve
        elif method == "CH":
            solve = M._cholesky_solve
        else:
            raise NotImplementedError(
                'Method may be "CH" or "LDL", not %s.' % method)
        rv = M.hstack(*[solve(I[:, i]) for i in range(I.cols)])
        if not sym:
            scale = (r1*rv[:, 0])[0, 0]
            rv /= scale
        return self._new(rv)

    def _eval_add(self, other):
        """If `other` is a SparseMatrix, add efficiently. Otherwise,
        do standard addition."""
        if not isinstance(other, SparseMatrix):
            return self + self._new(other)

        smat = {}
        zero = self._sympify(0)
        for key in set().union(self._smat.keys(), other._smat.keys()):
            sum = self._smat.get(key, zero) + other._smat.get(key, zero)
            if sum != 0:
                smat[key] = sum
        return self._new(self.rows, self.cols, smat)

    def _eval_col_insert(self, icol, other):
        if not isinstance(other, SparseMatrix):
            other = SparseMatrix(other)
        new_smat = {}
        # make room for the new rows
        for key, val in self._smat.items():
            row, col = key
            if col >= icol:
                col += other.cols
            new_smat[(row, col)] = val
        # add other's keys
        for key, val in other._smat.items():
            row, col = key
            new_smat[(row, col + icol)] = val
        return self._new(self.rows, self.cols + other.cols, new_smat)

    def _eval_conjugate(self):
        smat = {key: val.conjugate() for key,val in self._smat.items()}
        return self._new(self.rows, self.cols, smat)

    def _eval_extract(self, rowsList, colsList):
        """
        Extract a submatrix from the current matrix.
        
        This function extracts a submatrix by specifying rows and columns to include. It handles cases where the requested submatrix has fewer elements than the original matrix and optimizes the extraction process based on the size of the requested submatrix.
        
        Parameters:
        rowsList (list): A list of row indices to include in the submatrix.
        colsList (list): A list of column indices to include in the submatrix.
        
        Returns:
        Matrix: A new matrix
        """

        urow = list(uniq(rowsList))
        ucol = list(uniq(colsList))
        smat = {}
        if len(urow)*len(ucol) < len(self._smat):
            # there are fewer elements requested than there are elements in the matrix
            for i, r in enumerate(urow):
                for j, c in enumerate(ucol):
                    smat[i, j] = self._smat.get((r, c), 0)
        else:
            # most of the request will be zeros so check all of self's entries,
            # keeping only the ones that are desired
            for rk, ck in self._smat:
                if rk in urow and ck in ucol:
                    smat[(urow.index(rk), ucol.index(ck))] = self._smat[(rk, ck)]

        rv = self._new(len(urow), len(ucol), smat)
        # rv is nominally correct but there might be rows/cols
        # which require duplication
        if len(rowsList) != len(urow):
            for i, r in enumerate(rowsList):
                i_previous = rowsList.index(r)
                if i_previous != i:
                    rv = rv.row_insert(i, rv.row(i_previous))
        if len(colsList) != len(ucol):
            for i, c in enumerate(colsList):
                i_previous = colsList.index(c)
                if i_previous != i:
                    rv = rv.col_insert(i, rv.col(i_previous))
        return rv

    def _eval_has(self, *patterns):
        """
        Evaluates whether the matrix has any elements that match the given patterns.
        
        Parameters:
        *patterns (sympy expressions): Patterns to match against the matrix elements.
        
        Returns:
        bool: True if any element in the matrix matches the given patterns, False otherwise.
        
        Explanation:
        This function checks if any element in the matrix matches the given patterns. It first checks if the matrix has any zeros, and if so, it checks if `S.Zero` matches the given patterns. If the matrix
        """

        # if the matrix has any zeros, see if S.Zero
        # has the pattern.  If _smat is full length,
        # the matrix has no zeros.
        zhas = S.Zero.has(*patterns)
        if len(self._smat) == self.rows*self.cols:
            zhas = False
        return any(self[key].has(*patterns) for key in self._smat) or zhas

    def _eval_is_Identity(self):
        if not all(self[i, i] == 1 for i in range(self.rows)):
            return False
        return len(self._smat) == self.rows

    def _eval_is_symmetric(self, simpfunc):
        diff = (self - self.T).applyfunc(simpfunc)
        return len(diff.values()) == 0

    def _eval_matrix_mul(self, other):
        """Fast multiplication exploiting the sparsity of the matrix."""
        if not isinstance(other, SparseMatrix):
            return self*self._new(other)

        # if we made it here, we're both sparse matrices
        # create quick lookups for rows and cols
        row_lookup = defaultdict(dict)
        for (i,j), val in self._smat.items():
            row_lookup[i][j] = val
        col_lookup = defaultdict(dict)
        for (i,j), val in other._smat.items():
            col_lookup[j][i] = val

        smat = {}
        for row in row_lookup.keys():
            for col in col_lookup.keys():
                # find the common indices of non-zero entries.
                # these are the only things that need to be multiplied.
                indices = set(col_lookup[col].keys()) & set(row_lookup[row].keys())
                if indices:
                    val = sum(row_lookup[row][k]*col_lookup[col][k] for k in indices)
                    smat[(row, col)] = val
        return self._new(self.rows, other.cols, smat)

    def _eval_row_insert(self, irow, other):
        if not isinstance(other, SparseMatrix):
            other = SparseMatrix(other)
        new_smat = {}
        # make room for the new rows
        for key, val in self._smat.items():
            row, col = key
            if row >= irow:
                row += other.rows
            new_smat[(row, col)] = val
        # add other's keys
        for key, val in other._smat.items():
            row, col = key
            new_smat[(row + irow, col)] = val
        return self._new(self.rows + other.rows, self.cols, new_smat)

    def _eval_scalar_mul(self, other):
        return self.applyfunc(lambda x: x*other)

    def _eval_scalar_rmul(self, other):
        return self.applyfunc(lambda x: other*x)

    def _eval_transpose(self):
        """Returns the transposed SparseMatrix of this SparseMatrix.

        Examples
        ========

        >>> from sympy.matrices import SparseMatrix
        >>> a = SparseMatrix(((1, 2), (3, 4)))
        >>> a
        Matrix([
        [1, 2],
        [3, 4]])
        >>> a.T
        Matrix([
        [1, 3],
        [2, 4]])
        """
        smat = {(j,i): val for (i,j),val in self._smat.items()}
        return self._new(self.cols, self.rows, smat)

    def _eval_values(self):
        return [v for k,v in self._smat.items() if not v.is_zero]

    def _LDL_solve(self, rhs):
        # for speed reasons, this is not uncommented, but if you are
        # having difficulties, try uncommenting to make sure that the
        # input matrix is symmetric

        #assert self.is_symmetric()
        L, D = self._LDL_sparse()
        Z = L._lower_triangular_solve(rhs)
        Y = D._diagonal_solve(Z)
        return L.T._upper_triangular_solve(Y)

    def _LDL_sparse(self):
        """Algorithm for numeric LDL factization, exploiting sparse structure.
        """
        Lrowstruc = self.row_structure_symbolic_cholesky()
        L = self.eye(self.rows)
        D = self.zeros(self.rows, self.cols)

        for i in range(len(Lrowstruc)):
            for j in Lrowstruc[i]:
                if i != j:
                    L[i, j] = self[i, j]
                    summ = 0
                    for p1 in Lrowstruc[i]:
                        if p1 < j:
                            for p2 in Lrowstruc[j]:
                                if p2 < j:
                                    if p1 == p2:
                                        summ += L[i, p1]*L[j, p1]*D[p1, p1]
                                else:
                                    break
                        else:
                            break
                    L[i, j] -= summ
                    
