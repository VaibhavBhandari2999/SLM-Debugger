from __future__ import print_function, division

from mpmath.libmp.libmpf import prec_to_dps

from sympy.assumptions.refine import refine
from sympy.core.add import Add
from sympy.core.basic import Basic, Atom
from sympy.core.expr import Expr
from sympy.core.function import expand_mul
from sympy.core.power import Pow
from sympy.core.symbol import (Symbol, Dummy, symbols,
    _uniquely_named_symbol)
from sympy.core.numbers import Integer, ilcm, mod_inverse, Float
from sympy.core.singleton import S
from sympy.core.sympify import sympify
from sympy.functions.elementary.miscellaneous import sqrt, Max, Min
from sympy.functions import Abs, exp, factorial
from sympy.polys import PurePoly, roots, cancel, gcd
from sympy.printing import sstr
from sympy.simplify import simplify as _simplify, signsimp, nsimplify
from sympy.core.compatibility import reduce, as_int, string_types, Callable

from sympy.utilities.iterables import flatten, numbered_symbols
from sympy.core.decorators import call_highest_priority
from sympy.core.compatibility import (is_sequence, default_sort_key, range,
    NotIterable)

from sympy.utilities.exceptions import SymPyDeprecationWarning

from types import FunctionType

from .common import (a2idx, classof, MatrixError, ShapeError,
        NonSquareMatrixError, MatrixCommon)


def _iszero(x):
    """Returns True if x is zero."""
    try:
        return x.is_zero
    except AttributeError:
        return None


def _is_zero_after_expand_mul(x):
    """Tests by expand_mul only, suitable for polynomials and rational
    functions."""
    return expand_mul(x) == 0


class DeferredVector(Symbol, NotIterable):
    """A vector whose components are deferred (e.g. for use with lambdify)

    Examples
    ========

    >>> from sympy import DeferredVector, lambdify
    >>> X = DeferredVector( 'X' )
    >>> X
    X
    >>> expr = (X[0] + 2, X[2] + 3)
    >>> func = lambdify( X, expr)
    >>> func( [1, 2, 3] )
    (3, 6)
    """

    def __getitem__(self, i):
        """
        Retrieve a component of the vector.
        
        This method returns the symbol representing the i-th component of the vector.
        
        Parameters:
        i (int): The index of the component to retrieve. Negative indices are not allowed and will raise an IndexError.
        
        Returns:
        Symbol: A symbolic representation of the vector component.
        
        Raises:
        IndexError: If the index is negative.
        """

        if i == -0:
            i = 0
        if i < 0:
            raise IndexError('DeferredVector index out of range')
        component_name = '%s[%d]' % (self.name, i)
        return Symbol(component_name)

    def __str__(self):
        return sstr(self)

    def __repr__(self):
        return "DeferredVector('%s')" % self.name


class MatrixDeterminant(MatrixCommon):
    """Provides basic matrix determinant operations.
    Should not be instantiated directly."""

    def _eval_berkowitz_toeplitz_matrix(self):
        """Return (A,T) where T the Toeplitz matrix used in the Berkowitz algorithm
        corresponding to `self` and A is the first principal submatrix."""

        # the 0 x 0 case is trivial
        if self.rows == 0 and self.cols == 0:
            return self._new(1,1, [S.One])

        #
        # Partition self = [ a_11  R ]
        #                  [ C     A ]
        #

        a, R = self[0,0],   self[0, 1:]
        C, A = self[1:, 0], self[1:,1:]

        #
        # The Toeplitz matrix looks like
        #
        #  [ 1                                     ]
        #  [ -a         1                          ]
        #  [ -RC       -a        1                 ]
        #  [ -RAC     -RC       -a       1         ]
        #  [ -RA**2C -RAC      -RC      -a       1 ]
        #  etc.

        # Compute the diagonal entries.
        # Because multiplying matrix times vector is so much
        # more efficient than matrix times matrix, recursively
        # compute -R * A**n * C.
        diags = [C]
        for i in range(self.rows - 2):
            diags.append(A * diags[i])
        diags = [(-R*d)[0, 0] for d in diags]
        diags = [S.One, -a] + diags

        def entry(i,j):
            """
            Generate the entry of a tridiagonal matrix.
            
            This function returns the value of the entry at position (i, j) of a tridiagonal matrix.
            
            Parameters
            ----------
            i : int
            The row index of the matrix entry.
            j : int
            The column index of the matrix entry.
            
            Returns
            -------
            S.Zero : sympy.core.numbers.Zero
            If j > i, indicating that the entry is outside the tridiagonal band.
            diags[i - j] : symp
            """

            if j > i:
                return S.Zero
            return diags[i - j]

        toeplitz = self._new(self.cols + 1, self.rows, entry)
        return (A, toeplitz)

    def _eval_berkowitz_vector(self):
        """ Run the Berkowitz algorithm and return a vector whose entries
            are the coefficients of the characteristic polynomial of `self`.

            Given N x N matrix, efficiently compute
            coefficients of characteristic polynomials of 'self'
            without division in the ground domain.

            This method is particularly useful for computing determinant,
            principal minors and characteristic polynomial when 'self'
            has complicated coefficients e.g. polynomials. Semi-direct
            usage of this algorithm is also important in computing
            efficiently sub-resultant PRS.

            Assuming that M is a square matrix of dimension N x N and
            I is N x N identity matrix, then the Berkowitz vector is
            an N x 1 vector whose entries are coefficients of the
            polynomial

                           charpoly(M) = det(t*I - M)

            As a consequence, all polynomials generated by Berkowitz
            algorithm are monic.

           For more information on the implemented algorithm refer to:

           [1] S.J. Berkowitz, On computing the determinant in small
               parallel time using a small number of processors, ACM,
               Information Processing Letters 18, 1984, pp. 147-150

           [2] M. Keber, Division-Free computation of sub-resultants
               using Bezout matrices, Tech. Report MPI-I-2006-1-006,
               Saarbrucken, 2006
        """

        # handle the trivial cases
        if self.rows == 0 and self.cols == 0:
            return self._new(1, 1, [S.One])
        elif self.rows == 1 and self.cols == 1:
            return self._new(2, 1, [S.One, -self[0,0]])

        submat, toeplitz = self._eval_berkowitz_toeplitz_matrix()
        return toeplitz * submat._eval_berkowitz_vector()

    def _eval_det_bareiss(self):
        """Compute matrix determinant using Bareiss' fraction-free
        algorithm which is an extension of the well known Gaussian
        elimination method. This approach is best suited for dense
        symbolic matrices and will result in a determinant with
        minimal number of fractions. It means that less term
        rewriting is needed on resulting formulae.

        TODO: Implement algorithm for sparse matrices (SFF),
        http://www.eecis.udel.edu/~saunders/papers/sffge/it5.ps.
        """

        # Recursively implemented Bareiss' algorithm as per Deanna Richelle Leggett's
        # thesis http://www.math.usm.edu/perry/Research/Thesis_DRL.pdf
        def bareiss(mat, cumm=1):
            """
            Compute the determinant of a matrix using Bareiss's algorithm.
            
            Parameters
            ----------
            mat : Matrix
            The matrix for which the determinant is to be computed.
            cumm : int, optional
            The cumulative product used in the algorithm, defaults to 1.
            
            Returns
            -------
            det : Expr
            The determinant of the matrix.
            
            Notes
            -----
            This function uses Bareiss's algorithm to compute the determinant of a matrix.
            It recursively reduces the matrix size by one row and one column at each step,
            """

            if mat.rows == 0:
                return S.One
            elif mat.rows == 1:
                return mat[0, 0]

            # find a pivot and extract the remaining matrix
            # With the default iszerofunc, _find_reasonable_pivot slows down
            # the computation by the factor of 2.5 in one test.
            # Relevant issues: #10279 and #13877.
            pivot_pos, pivot_val, _, _ = _find_reasonable_pivot(mat[:, 0],
                                         iszerofunc=_is_zero_after_expand_mul)
            if pivot_pos == None:
                return S.Zero

            # if we have a valid pivot, we'll do a "row swap", so keep the
            # sign of the det
            sign = (-1) ** (pivot_pos % 2)

            # we want every row but the pivot row and every column
            rows = list(i for i in range(mat.rows) if i != pivot_pos)
            cols = list(range(mat.cols))
            tmp_mat = mat.extract(rows, cols)

            def entry(i, j):
                ret = (pivot_val*tmp_mat[i, j + 1] - mat[pivot_pos, j + 1]*tmp_mat[i, 0]) / cumm
                if not ret.is_Atom:
                    cancel(ret)
                return ret

            return sign*bareiss(self._new(mat.rows - 1, mat.cols - 1, entry), pivot_val)

        return cancel(bareiss(self))

    def _eval_det_berkowitz(self):
        """ Use the Berkowitz algorithm to compute the determinant."""
        berk_vector = self._eval_berkowitz_vector()
        return (-1)**(len(berk_vector) - 1) * berk_vector[-1]

    def _eval_det_lu(self, iszerofunc=_iszero, simpfunc=None):
        """ Computes the determinant of a matrix from its LU decomposition.
        This function uses the LU decomposition computed by
        LUDecomposition_Simple().

        The keyword arguments iszerofunc and simpfunc are passed to
        LUDecomposition_Simple().
        iszerofunc is a callable that returns a boolean indicating if its
        input is zero, or None if it cannot make the determination.
        simpfunc is a callable that simplifies its input.
        The default is simpfunc=None, which indicate that the pivot search
        algorithm should not attempt to simplify any candidate pivots.
        If simpfunc fails to simplify its input, then it must return its input
        instead of a copy."""

        if self.rows == 0:
            return S.One
            # sympy/matrices/tests/test_matrices.py contains a test that
            # suggests that the determinant of a 0 x 0 matrix is one, by
            # convention.

        lu, row_swaps = self.LUdecomposition_Simple(iszerofunc=iszerofunc, simpfunc=None)
        # P*A = L*U => det(A) = det(L)*det(U)/det(P) = det(P)*det(U).
        # Lower triangular factor L encoded in lu has unit diagonal => det(L) = 1.
        # P is a permutation matrix => det(P) in {-1, 1} => 1/det(P) = det(P).
        # LUdecomposition_Simple() returns a list of row exchange index pairs, rather
        # than a permutation matrix, but det(P) = (-1)**len(row_swaps).

        # Avoid forming the potentially time consuming  product of U's diagonal entries
        # if the product is zero.
        # Bottom right entry of U is 0 => det(A) = 0.
        # It may be impossible to determine if this entry of U is zero when it is symbolic.
        if iszerofunc(lu[lu.rows-1, lu.rows-1]):
            return S.Zero

        # Compute det(P)
        det = -S.One if len(row_swaps)%2 else S.One

        # Compute det(U) by calculating the product of U's diagonal entries.
        # The upper triangular portion of lu is the upper triangular portion of the
        # U factor in the LU decomposition.
        for k in range(lu.rows):
            det *= lu[k, k]

        # return det(P)*det(U)
        return det

    def _eval_determinant(self):
        """Assumed to exist by matrix expressions; If we subclass
        MatrixDeterminant, we can fully evaluate determinants."""
        return self.det()

    def adjugate(self, method="berkowitz"):
        """Returns the adjugate, or classical adjoint, of
        a matrix.  That is, the transpose of the matrix of cofactors.


        http://en.wikipedia.org/wiki/Adjugate

        See Also
        ========

        cofactor_matrix
        transpose
        """
        return self.cofactor_matrix(method).transpose()

    def charpoly(self, x='lambda', simplify=_simplify):
        """Computes characteristic polynomial det(x*I - self) where I is
        the identity matrix.

        A PurePoly is returned, so using different variables for ``x`` does
        not affect the comparison or the polynomials:

        Examples
        ========

        >>> from sympy import Matrix
        >>> from sympy.abc import x, y
        >>> A = Matrix([[1, 3], [2, 0]])
        >>> A.charpoly(x) == A.charpoly(y)
        True

        Specifying ``x`` is optional; a symbol named ``lambda`` is used by
        default (which looks good when pretty-printed in unicode):

        >>> A.charpoly().as_expr()
        lambda**2 - lambda - 6

        And if ``x`` clashes with an existing symbol, underscores will
        be preppended to the name to make it unique:

        >>> A = Matrix([[1, 2], [x, 0]])
        >>> A.charpoly(x).as_expr()
        _x**2 - _x - 2*x

        Whether you pass a symbol or not, the generator can be obtained
        with the gen attribute since it may not be the same as the symbol
        that was passed:

        >>> A.charpoly(x).gen
        _x
        >>> A.charpoly(x).gen == x
        False

        Notes
        =====

        The Samuelson-Berkowitz algorithm is used to compute
        the characteristic polynomial efficiently and without any
        division operations.  Thus the characteristic polynomial over any
        commutative ring without zero divisors can be computed.

        See Also
        ========

        det
        """

        if self.rows != self.cols:
            raise NonSquareMatrixError()

        berk_vector = self._eval_berkowitz_vector()
        x = _uniquely_named_symbol(x, berk_vector)
        return PurePoly([simplify(a) for a in berk_vector], x)

    def cofactor(self, i, j, method="berkowitz"):
        """Calculate the cofactor of an element.

        See Also
        ========

        cofactor_matrix
        minor
        minor_submatrix
        """

        if self.rows != self.cols or self.rows < 1:
            raise NonSquareMatrixError()

        return (-1)**((i + j) % 2) * self.minor(i, j, method)

    def cofactor_matrix(self, method="berkowitz"):
        """Return a matrix containing the cofactor of each element.

        See Also
        ========

        cofactor
        minor
        minor_submatrix
        adjugate
        """

        if self.rows != self.cols or self.rows < 1:
            raise NonSquareMatrixError()

        return self._new(self.rows, self.cols,
                         lambda i, j: self.cofactor(i, j, method))

    def det(self, method="bareiss"):
        """Computes the determinant of a matrix.  If the matrix
        is at most 3x3, a hard-coded formula is used.
        Otherwise, the determinant using the method `method`.


        Possible values for "method":
          bareis
          berkowitz
          lu
        """

        # sanitize `method`
        method = method.lower()
        if method == "bareis":
            method = "bareiss"
        if method == "det_lu":
            method = "lu"
        if method not in ("bareiss", "berkowitz", "lu"):
            raise ValueError("Determinant method '%s' unrecognized" % method)

        # if methods were made internal and all determinant calculations
        # passed through here, then these lines could be factored out of
        # the method routines
        if self.rows != self.cols:
            raise NonSquareMatrixError()

        n = self.rows
        if n == 0:
            return S.One
        elif n == 1:
            return self[0,0]
        elif n == 2:
            return self[0, 0] * self[1, 1] - self[0, 1] * self[1, 0]
        elif n == 3:
            return  (self[0, 0] * self[1, 1] * self[2, 2]
                   + self[0, 1] * self[1, 2] * self[2, 0]
                   + self[0, 2] * self[1, 0] * self[2, 1]
                   - self[0, 2] * self[1, 1] * self[2, 0]
                   - self[0, 0] * self[1, 2] * self[2, 1]
                   - self[0, 1] * self[1, 0] * self[2, 2])

        if method == "bareiss":
            return self._eval_det_bareiss()
        elif method == "berkowitz":
            return self._eval_det_berkowitz()
        elif method == "lu":
            return self._eval_det_lu()

    def minor(self, i, j, method="berkowitz"):
        """Return the (i,j) minor of `self`.  That is,
        return the determinant of the matrix obtained by deleting
        the `i`th row and `j`th column from `self`.

        See Also
        ========

        minor_submatrix
        cofactor
        det
        """

        if self.rows != self.cols or self.rows < 1:
            raise NonSquareMatrixError()

        return self.minor_submatrix(i, j).det(method=method)

    def minor_submatrix(self, i, j):
        """Return the submatrix obtained by removing the `i`th row
        and `j`th column from `self`.

        See Also
        ========

        minor
        cofactor
        """

        if i < 0:
            i += self.rows
        if j < 0:
            j += self.cols

        if not 0 <= i < self.rows or not 0 <= j < self.cols:
            raise ValueError("`i` and `j` must satisfy 0 <= i < `self.rows` "
                             "(%d)" % self.rows + "and 0 <= j < `self.cols` (%d)." % self.cols)

        rows = [a for a in range(self.rows) if a != i]
        cols = [a for a in range(self.cols) if a != j]
        return self.extract(rows, cols)


class MatrixReductions(MatrixDeterminant):
    """Provides basic matrix row/column operations.
    Should not be instantiated directly."""

    def _eval_col_op_swap(self, col1, col2):
        def entry(i, j):
            """
            Generate an entry in a matrix after applying a row operation.
            
            This function computes the value of an entry in a matrix after performing a specific row operation.
            
            Parameters:
            i (int): The row index of the entry.
            j (int): The column index of the entry.
            
            Keyword Arguments:
            col (int): The column index of the pivot element.
            col2 (int): The column index to be added to the pivot row.
            k (float): The scalar multiple for the column
            """

            if j == col1:
                return self[i, col2]
            elif j == col2:
                return self[i, col1]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_col_op_multiply_col_by_const(self, col, k):
        def entry(i, j):
            if j == col:
                return k * self[i, j]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_col_op_add_multiple_to_other_col(self, col, k, col2):
        def entry(i, j):
            if j == col:
                return self[i, j] + k * self[i, col2]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_row_op_swap(self, row1, row2):
        """
        Swaps two rows in the matrix.
        
        This function swaps the entries of two specified rows in the matrix.
        
        Parameters:
        row1 (int): The index of the first row to swap.
        row2 (int): The index of the second row to swap.
        
        Returns:
        Matrix: A new matrix with the specified rows swapped. The original matrix remains unchanged.
        """

        def entry(i, j):
            if i == row1:
                return self[row2, j]
            elif i == row2:
                return self[row1, j]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_row_op_multiply_row_by_const(self, row, k):
        def entry(i, j):
            if i == row:
                return k * self[i, j]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_row_op_add_multiple_to_other_row(self, row, k, row2):
        def entry(i, j):
            if i == row:
                return self[i, j] + k * self[row2, j]
            return self[i, j]
        return self._new(self.rows, self.cols, entry)

    def _eval_echelon_form(self, iszerofunc, simpfunc):
        """Returns (mat, swaps) where `mat` is a row-equivalent matrix
        in echelon form and `swaps` is a list of row-swaps performed."""
        reduced, pivot_cols, swaps = self._row_reduce(iszerofunc, simpfunc,
                                                      normalize_last=True,
                                                      normalize=False,
                                                      zero_above=False)
        return reduced, pivot_cols, swaps

    def _eval_is_echelon(self, iszerofunc):
        """
        Evaluates if the matrix is in Echelon form.
        
        Parameters:
        iszerofunc (callable): A function that checks if an element is zero.
        
        Returns:
        bool: True if the matrix is in Echelon form, False otherwise.
        
        Explanation:
        The matrix is in Echelon form if:
        1. All zero rows are at the bottom.
        2. The leading coefficient (pivot) of a non-zero row is to the right of the leading coefficient
        """

        if self.rows <= 0 or self.cols <= 0:
            return True
        zeros_below = all(iszerofunc(t) for t in self[1:, 0])
        if iszerofunc(self[0, 0]):
            return zeros_below and self[:, 1:]._eval_is_echelon(iszerofunc)
        return zeros_below and self[1:, 1:]._eval_is_echelon(iszerofunc)

    def _eval_rref(self, iszerofunc, simpfunc, normalize_last=True):
        reduced, pivot_cols, swaps = self._row_reduce(iszerofunc, simpfunc,
                                                      normalize_last, normalize=True,
                                                      zero_above=True)
        return reduced, pivot_cols

    def _normalize_op_args(self, op, col, k, col1, col2, error_str="col"):
        """Validate the arguments for a row/column operation.  `error_str`
        can be one of "row" or "col" depending on the arguments being parsed."""
        if op not in ["n->kn", "n<->m", "n->n+km"]:
            raise ValueError("Unknown {} operation '{}'. Valid col operations "
                             "are 'n->kn', 'n<->m', 'n->n+km'".format(error_str, op))

        # normalize and validate the arguments
        if op == "n->kn":
            col = col if col is not None else col1
            if col is None or k is None:
                raise ValueError("For a {0} operation 'n->kn' you must provide the "
                                 "kwargs `{0}` and `k`".format(error_str))
            if not 0 <= col <= self.cols:
                raise ValueError("This matrix doesn't have a {} '{}'".format(error_str, col))

        if op == "n<->m":
            # we need two cols to swap. It doesn't matter
            # how they were specified, so gather them together and
            # remove `None`
            cols = set((col, k, col1, col2)).difference([None])
            if len(cols) > 2:
                # maybe the user left `k` by mistake?
                cols = set((col, col1, col2)).difference([None])
            if len(cols) != 2:
                raise ValueError("For a {0} operation 'n<->m' you must provide the "
                                 "kwargs `{0}1` and `{0}2`".format(error_str))
            col1, col2 = cols
            if not 0 <= col1 <= self.cols:
                raise ValueError("This matrix doesn't have a {} '{}'".format(error_str, col1))
            if not 0 <= col2 <= self.cols:
                raise ValueError("This matrix doesn't have a {} '{}'".format(error_str, col2))

        if op == "n->n+km":
            col = col1 if col is None else col
            col2 = col1 if col2 is None else col2
            if col is None or col2 is None or k is None:
                raise ValueError("For a {0} operation 'n->n+km' you must provide the "
                                 "kwargs `{0}`, `k`, and `{0}2`".format(error_str))
            if col == col2:
                raise ValueError("For a {0} operation 'n->n+km' `{0}` and `{0}2` must "
                                 "be different.".format(error_str))
            if not 0 <= col <= self.cols:
                raise ValueError("This matrix doesn't have a {} '{}'".format(error_str, col))
            if not 0 <= col2 <= self.cols:
                raise ValueError("This matrix doesn't have a {} '{}'".format(error_str, col2))

        return op, col, k, col1, col2

    def _permute_complexity_right(self, iszerofunc):
        """Permute columns with complicated elements as
        far right as they can go.  Since the `sympy` row reduction
        algorithms start on the left, having complexity right-shifted
        speeds things up.

        Returns a tuple (mat, perm) where perm is a permutation
        of the columns to perform to shift the complex columns right, and mat
        is the permuted matrix."""

        def complexity(i):
            """
            Determine the complexity of a column in a matrix.
            
            This function evaluates the complexity of a column in a matrix by counting the number of elements whose zero-ness cannot be determined.
            
            Parameters:
            i (int): The index of the column to be evaluated.
            
            Returns:
            int: The complexity of the column, defined as the count of elements with undetermined zero-ness.
            
            Notes:
            - The function uses `iszerofunc` to check if an element's zero-ness can be
            """

            # the complexity of a column will be judged by how many
            # element's zero-ness cannot be determined
            return sum(1 if iszerofunc(e) is None else 0 for e in self[:, i])
        complex = [(complexity(i), i) for i in range(self.cols)]
        perm = [j for (i, j) in sorted(complex)]

        return (self.permute(perm, orientation='cols'), perm)

    def _row_reduce(self, iszerofunc, simpfunc, normalize_last=True,
                    normalize=True, zero_above=True):
        """Row reduce `self` and return a tuple (rref_matrix,
        pivot_cols, swaps) where pivot_cols are the pivot columns
        and swaps are any row swaps that were used in the process
        of row reduction.

        Parameters
        ==========

        iszerofunc : determines if an entry can be used as a pivot
        simpfunc : used to simplify elements and test if they are
            zero if `iszerofunc` returns `None`
        normalize_last : indicates where all row reduction should
            happen in a fraction-free manner and then the rows are
            normalized (so that the pivots are 1), or whether
            rows should be normalized along the way (like the naive
            row reduction algorithm)
        normalize : whether pivot rows should be normalized so that
            the pivot value is 1
        zero_above : whether entries above the pivot should be zeroed.
            If `zero_above=False`, an echelon matrix will be returned.
        """
        rows, cols = self.rows, self.cols
        mat = list(self)
        def get_col(i):
            return mat[i::cols]

        def row_swap(i, j):
            mat[i*cols:(i + 1)*cols], mat[j*cols:(j + 1)*cols] = \
                mat[j*cols:(j + 1)*cols], mat[i*cols:(i + 1)*cols]

        def cross_cancel(a, i, b, j):
            """Does the row op row[i] = a*row[i] - b*row[j]"""
            q = (j - i)*cols
            for p in range(i*cols, (i + 1)*cols):
                mat[p] = a*mat[p] - b*mat[p + q]

        piv_row, piv_col = 0, 0
        pivot_cols = []
        swaps = []
        # use a fraction free method to zero above and below each pivot
        while piv_col < cols and piv_row < rows:
            pivot_offset, pivot_val, \
            assumed_nonzero, newly_determined = _find_reasonable_pivot(
                get_col(piv_col)[piv_row:], iszerofunc, simpfunc)

            # _find_reasonable_pivot may have simplified some things
            # in the process.  Let's not let them go to waste
            for (offset, val) in newly_determined:
                offset += piv_row
                mat[offset*cols + piv_col] = val

            if pivot_offset is None:
                piv_col += 1
                continue

            pivot_cols.append(piv_col)
            if pivot_offset != 0:
                row_swap(piv_row, pivot_offset + piv_row)
                swaps.append((piv_row, pivot_offset + piv_row))

            # if we aren't normalizing last, we normalize
            # before we zero the other rows
            if normalize_last is False:
                i, j = piv_row, piv_col
                mat[i*cols + j] = S.One
                for p in range(i*cols + j + 1, (i + 1)*cols):
                    mat[p] = mat[p] / pivot_val
                # after normalizing, the pivot value is 1
                pivot_val = S.One

            # zero above and below the pivot
            for row in range(rows):
                # don't zero our current row
                if row == piv_row:
                    continue
                # don't zero above the pivot unless we're told.
                if zero_above is False and row < piv_row:
                    continue
                # if we're already a zero, don't do anything
                val = mat[row*cols + piv_col]
                if iszerofunc(val):
                    continue

                cross_cancel(pivot_val, row, val, piv_row)
            piv_row += 1

        # normalize each row
        if normalize_last is True and normalize is True:
            for piv_i, piv_j in enumerate(pivot_cols):
                pivot_val = mat[piv_i*cols + piv_j]
                mat[piv_i*cols + piv_j] = S.One
                for p in range(piv_i*cols + piv_j + 1, (piv_i + 1)*cols):
                    mat[p] = mat[p] / pivot_val

        return self._new(self.rows, self.cols, mat), tuple(pivot_cols), tuple(swaps)

    def echelon_form(self, iszerofunc=_iszero, simplify=False, with_pivots=False):
        """Returns a matrix row-equivalent to `self` that is
        in echelon form.  Note that echelon form of a matrix
        is *not* unique, however, properties like the row
        space and the null space are preserved."""
        simpfunc = simplify if isinstance(
            simplify, FunctionType) else _simplify

        mat, pivots, swaps = self._eval_echelon_form(iszerofunc, simpfunc)
        if with_pivots:
            return mat, pivots
        return mat

    def elementary_col_op(self, op="n->kn", col=None, k=None, col1=None, col2=None):
        """Performs the elementary column operation `op`.

        `op` may be one of

            * "n->kn" (column n goes to k*n)
            * "n<->m" (swap column n and column m)
            * "n->n+km" (column n goes to column n + k*column m)

        Parameters
        =========

        op : string; the elementary row operation
        col : the column to apply the column operation
        k : the multiple to apply in the column operation
        col1 : one column of a column swap
        col2 : second column of a column swap or column "m" in the column operation
               "n->n+km"
        """

        op, col, k, col1, col2 = self._normalize_op_args(op, col, k, col1, col2, "col")

        # now that we've validated, we're all good to dispatch
        if op == "n->kn":
            return self._eval_col_op_multiply_col_by_const(col, k)
        if op == "n<->m":
            return self._eval_col_op_swap(col1, col2)
        if op == "n->n+km":
            return self._eval_col_op_add_multiple_to_other_col(col, k, col2)

    def elementary_row_op(self, op="n->kn", row=None, k=None, row1=None, row2=None):
        """Performs the elementary row operation `op`.

        `op` may be one of

            * "n->kn" (row n goes to k*n)
            * "n<->m" (swap row n and row m)
            * "n->n+km" (row n goes to row n + k*row m)

        Parameters
        ==========

        op : string; the elementary row operation
        row : the row to apply the row operation
        k : the multiple to apply in the row operation
        row1 : one row of a row swap
        row2 : second row of a row swap or row "m" in the row operation
               "n->n+km"
        """

        op, row, k, row1, row2 = self._normalize_op_args(op, row, k, row1, row2, "row")

        # now that we've validated, we're all good to dispatch
        if op == "n->kn":
            return self._eval_row_op_multiply_row_by_const(row, k)
        if op == "n<->m":
            return self._eval_row_op_swap(row1, row2)
        if op == "n->n+km":
            return self._eval_row_op_add_multiple_to_other_row(row, k, row2)

    @property
    def is_echelon(self, iszerofunc=_iszero):
        """Returns `True` if the matrix is in echelon form.
        That is, all rows of zeros are at the bottom, and below
        each leading non-zero in a row are exclusively zeros."""

        return self._eval_is_echelon(iszerofunc)

    def rank(self, iszerofunc=_iszero, simplify=False):
        """
        Returns the rank of a matrix

        >>> from sympy import Matrix
        >>> from sympy.abc import x
        >>> m = Matrix([[1, 2], [x, 1 - 1/x]])
        >>> m.rank()
        2
        >>> n = Matrix(3, 3, range(1, 10))
        >>> n.rank()
        2
        """
        simpfunc = simplify if isinstance(
            simplify, FunctionType) else _simplify

        # for small matrices, we compute the rank explicitly
        # if is_zero on elements doesn't answer the question
        # for small matrices, we fall back to the full routine.
        if self.rows <= 0 or self.cols <= 0:
            return 0
        if self.rows <= 1 or self.cols <= 1:
            zeros = [iszerofunc(x) for x in self]
            if False in zeros:
                return 1
        if self.rows == 2 and self.cols == 2:
            zeros = [iszerofunc(x) for x in self]
            if not False in zeros and not None in zeros:
                return 0
            det = self.det()
            if iszerofunc(det) and False in zeros:
                return 1
            if iszerofunc(det) is False:
                return 2

        mat, _ = self._permute_complexity_right(iszerofunc=iszerofunc)
        echelon_form, pivots, swaps = mat._eval_echelon_form(iszerofunc=iszerofunc, simpfunc=simpfunc)
        return len(pivots)

    def rref(self, iszerofunc=_iszero, simplify=False, pivots=True, normalize_last=True):
        """Return reduced row-echelon form of matrix and indices of pivot vars.

        Parameters
        ==========

        iszerofunc : Function
            A function used for detecting whether an element can
            act as a pivot.  `lambda x: x.is_zero` is used by default.
        simplify : Function
            A function used to simplify elements when looking for a pivot.
            By default SymPy's `simplify`is used.
        pivots : True or False
            If `True`, a tuple containing the row-reduced matrix and a tuple
            of pivot columns is returned.  If `False` just the row-reduced
            matrix is returned.
        normalize_last : True or False
            If `True`, no pivots are normalized to `1` until after all entries
            above and below each pivot are zeroed.  This means the row
            reduction algorithm is fraction free until the very last step.
            If `False`, the naive row reduction procedure is used where
            each pivot is normalized to be `1` before row operations are
            used to zero above and below the pivot.

        Notes
        =====

        The default value of `normalize_last=True` can provide significant
        speedup to row reduction, especially on matrices with symbols.  However,
        if you depend on the form row reduction algorithm leaves entries
        of the matrix, set `noramlize_last=False`


        Examples
        ========

        >>> from sympy import Matrix
        >>> from sympy.abc import x
        >>> m = Matrix([[1, 2], [x, 1 - 1/x]])
        >>> m.rref()
        (Matrix([
        [1, 0],
        [0, 1]]), (0, 1))
        >>> rref_matrix, rref_pivots = m.rref()
        >>> rref_matrix
        Matrix([
        [1, 0],
        [0, 1]])
        >>> rref_pivots
        (0, 1)
        """
        simpfunc = simplify if isinstance(
            simplify, FunctionType) else _simplify

        ret, pivot_cols = self._eval_rref(iszerofunc=iszerofunc,
                                          simpfunc=simpfunc,
                                          normalize_last=normalize_last)
        if pivots:
            ret = (ret, pivot_cols)
        return ret


class MatrixSubspaces(MatrixReductions):
    """Provides methods relating to the fundamental subspaces
    of a matrix.  Should not be instantiated directly."""

    def columnspace(self, simplify=False):
        """Returns a list of vectors (Matrix objects) that span columnspace of self

        Examples
        ========

        >>> from sympy.matrices import Matrix
        >>> m = Matrix(3, 3, [1, 3, 0, -2, -6, 0, 3, 9, 6])
        >>> m
        Matrix([
        [ 1,  3, 0],
        [-2, -6, 0],
        [ 3,  9, 6]])
        >>> m.columnspace()
        [Matrix([
        [ 1],
        [-2],
        [ 3]]), Matrix([
        [0],
        [0],
        [6]])]

        See Also
        ========

        nullspace
        rowspace
        """
        reduced, pivots = self.echelon_form(simplify=simplify, with_pivots=True)

        return [self.col(i) for i in pivots]

    def nullspace(self, simplify=False):
        """Returns list of vectors (Matrix objects) that span nullspace of self

        Examples
        ========

        >>> from sympy.matrices import Matrix
        >>> m = Matrix(3, 3, [1, 3, 0, -2, -6, 0, 3, 9, 6])
        >>> m
        Matrix([
        [ 1,  3, 0],
        [-2, -6, 0],
        [ 3,  9, 6]])
        >>> m.nullspace()
        [Matrix([
        [-3],
        [ 1],
        [ 0]])]

        See Also
        ========

        columnspace
        rowspace
        """

        reduced, pivots = self.rref(simplify=simplify)

        free_vars = [i for i in range(self.cols) if i not in pivots]

        basis = []
        for free_var in free_vars:
            # for each free variable, we will set it to 1 and all others
            # to 0.  Then, we will use back substitution to solve the system
            vec = [S.Zero]*self.cols
            vec[free_var] = S.One
            for piv_row, piv_col in enumerate(pivots):
                vec[piv_col] -= reduced[piv_row, free_var]
            basis.append(vec)

        return [self._new(self.cols, 1, b) for b in basis]

    def rowspace(self, simplify=False):
        """Returns a list of vectors that span the row space of self."""

        reduced, pivots = self.echelon_form(simplify=simplify, with_pivots=True)

        return [reduced.row(i) for i in range(len(pivots))]

    @classmethod
    def orthogonalize(cls, *vecs, **kwargs):
        """Apply the Gram-Schmidt orthogonalization procedure
        to vectors supplied in `vecs`.

        Arguments
        =========

        vecs : vectors to be made orthogonal
        normalize : bool. Whether the returned vectors
                    should be renormalized to be unit vectors.
        """

        normalize = kwargs.get('normalize', False)

        def project(a, b):
            return b * (a.dot(b) / b.dot(b))

        def perp_to_subspace(vec, basis):
            """projects vec onto the subspace given
            by the orthogonal basis `basis`"""
            components = [project(vec, b) for b in basis]
            if len(basis) == 0:
                return vec
            return vec - reduce(lambda a, b: a + b, components)

        ret = []
        # make sure we start with a non-zero vector
        while len(vecs) > 0 and vecs[0].is_zero:
            del vecs[0]

        for vec in vecs:
            perp = perp_to_subspace(vec, ret)
            if not perp.is_zero:
                ret.append(perp)

        if normalize:
            ret = [vec / vec.norm() for vec in ret]

        return ret


class MatrixEigen(MatrixSubspaces):
    """Provides basic matrix eigenvalue/vector operations.
    Should not be instantiated directly."""

    _cache_is_diagonalizable = None
    _cache_eigenvects = None

    def diagonalize(self, reals_only=False, sort=False, normalize=False):
        """
        Return (P, D), where D is diagonal and

            D = P^-1 * M * P

        where M is current matrix.

        Parameters
        ==========

        reals_only : bool. Whether to throw an error if complex numbers are need
                     to diagonalize. (Default: False)
        sort : bool. Sort the eigenvalues along the diagonal. (Default: False)
        normalize : bool. If True, normalize the columns of P. (Default: False)

        Examples
        ========

        >>> from sympy import Matrix
        >>> m = Matrix(3, 3, [1, 2, 0, 0, 3, 0, 2, -4, 2])
        >>> m
        Matrix([
        [1,  2, 0],
        [0,  3, 0],
        [2, -4, 2]])
        >>> (P, D) = m.diagonalize()
        >>> D
        Matrix([
        [1, 0, 0],
        [0, 2, 0],
        [0, 0, 3]])
        >>> P
        Matrix([
        [-1, 0, -1],
        [ 0, 0, -1],
        [ 2, 1,  2]])
        >>> P.inv() * m * P
        Matrix([
        [1, 0, 0],
        [0, 2, 0],
        [0, 0, 3]])

        See Also
        ========

        is_diagonal
        is_diagonalizable
        """

        if not self.is_square:
            raise NonSquareMatrixError()

        if not self.is_diagonalizable(reals_only=reals_only, clear_cache=False):
            raise MatrixError("Matrix is not diagonalizable")

        eigenvecs = self._cache_eigenvects
        if eigenvecs is None:
            eigenvecs = self.eigenvects(simplify=True)

        if sort:
            eigenvecs = sorted(eigenvecs, key=default_sort_key)

        p_cols, diag = [], []
        for val, mult, basis in eigenvecs:
            diag += [val] * mult
            p_cols += basis

        if normalize:
            p_cols = [v / v.norm() for v in p_cols]

        return self.hstack(*p_cols), self.diag(*diag)

    def eigenvals(self, error_when_incomplete=True, **flags):
        """Return eigenvalues using the Berkowitz agorithm to compute
        the characteristic polynomial.

        Parameters
        ==========

        error_when_incomplete : bool
            Raise an error when not all eigenvalues are computed. This is
            caused by ``roots`` not returning a full list of eigenvalues.

        Since the roots routine doesn't always work well with Floats,
        they will be replaced with Rationals before calling that
        routine. If this is not desired, set flag ``rational`` to False.
        """
        mat = self
        if not mat:
            return {}
        if flags.pop('rational', True):
            if any(v.has(Float) for v in mat):
                mat = mat.applyfunc(lambda x: nsimplify(x, rational=True))

        flags.pop('simplify', None)  # pop unsupported flag
        eigs = roots(mat.charpoly(x=Dummy('x')), **flags)

        # make sure the algebraic multiplicty sums to the
        # size of the matrix
        if error_when_incomplete and (sum(eigs.values()) if
            isinstance(eigs, dict) else len(eigs)) != self.cols:
            raise MatrixError("Could not compute eigenvalues for {}".format(self))

        return eigs

    def eigenvects(self, error_when_incomplete=True, **flags):
        """Return list of triples (eigenval, multiplicity, basis).

        The flag ``simplify`` has two effects:
            1) if bool(simplify) is True, as_content_primitive()
            will be used to tidy up normalization artifacts;
            2) if nullspace needs simplification to compute the
            basis, the simplify flag will be passed on to the
            nullspace routine which will interpret it there.

        Parameters
        ==========

        error_when_incomplete : bool
            Raise an error when not all eigenvalues are computed. This is
            caused by ``roots`` not returning a full list of eigenvalues.

        If the matrix contains any Floats, they will be changed to Rationals
        for computation purposes, but the answers will be returned after being
        evaluated with evalf. If it is desired to removed small imaginary
        portions during the evalf step, pass a value for the ``chop`` flag.
        """
        from sympy.matrices import eye

        simplify = flags.get('simplify', True)
        if not isinstance(simplify, FunctionType):
            simpfunc = _simplify if simplify else lambda x: x
        primitive = flags.get('simplify', False)
        chop = flags.pop('chop', False)

        flags.pop('multiple', None)  # remove this if it's there

        mat = self
        # roots doesn't like Floats, so replace them with Rationals
        has_floats = any(v.has(Float) for v in self)
        if has_floats:
            mat = mat.applyfunc(lambda x: nsimplify(x, rational=True))

        def eigenspace(eigenval):
            """Get a basis for the eigenspace for a particular eigenvalue"""
            m = mat - self.eye(mat.rows) * eigenval
            ret = m.nullspace()
            # the nullspace for a real eigenvalue should be
            # non-trivial.  If we didn't 
