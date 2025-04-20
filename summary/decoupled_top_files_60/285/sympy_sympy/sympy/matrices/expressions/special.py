from sympy.assumptions.ask import ask, Q
from sympy.core.relational import Eq
from sympy.core.singleton import S
from sympy.core.sympify import _sympify
from sympy.functions.special.tensor_functions import KroneckerDelta
from sympy.matrices.common import NonInvertibleMatrixError
from .matexpr import MatrixExpr


class ZeroMatrix(MatrixExpr):
    """The Matrix Zero 0 - additive identity

    Examples
    ========

    >>> from sympy import MatrixSymbol, ZeroMatrix
    >>> A = MatrixSymbol('A', 3, 5)
    >>> Z = ZeroMatrix(3, 5)
    >>> A + Z
    A
    >>> Z*A.T
    0
    """
    is_ZeroMatrix = True

    def __new__(cls, m, n):
        """
        Construct a new matrix of dimensions m x n.
        
        Parameters:
        m (int or sympy expression): The number of rows in the matrix.
        n (int or sympy expression): The number of columns in the matrix.
        
        Returns:
        Matrix: A new matrix object with the specified dimensions.
        
        Notes:
        - The input values for m and n are first converted to sympy expressions.
        - The dimensions are validated using the `_check_dim` method.
        - The matrix is created using
        """

        m, n = _sympify(m), _sympify(n)
        cls._check_dim(m)
        cls._check_dim(n)

        return super().__new__(cls, m, n)

    @property
    def shape(self):
        return (self.args[0], self.args[1])

    def _eval_power(self, exp):
        # exp = -1, 0, 1 are already handled at this stage
        if (exp < 0) == True:
            raise NonInvertibleMatrixError("Matrix det == 0; not invertible")
        return self

    def _eval_transpose(self):
        return ZeroMatrix(self.cols, self.rows)

    def _eval_trace(self):
        return S.Zero

    def _eval_determinant(self):
        return S.Zero

    def _eval_inverse(self):
        raise NonInvertibleMatrixError("Matrix det == 0; not invertible.")

    def conjugate(self):
        return self

    def _entry(self, i, j, **kwargs):
        return S.Zero


class GenericZeroMatrix(ZeroMatrix):
    """
    A zero matrix without a specified shape

    This exists primarily so MatAdd() with no arguments can return something
    meaningful.
    """
    def __new__(cls):
        # super(ZeroMatrix, cls) instead of super(GenericZeroMatrix, cls)
        # because ZeroMatrix.__new__ doesn't have the same signature
        return super(ZeroMatrix, cls).__new__(cls)

    @property
    def rows(self):
        raise TypeError("GenericZeroMatrix does not have a specified shape")

    @property
    def cols(self):
        raise TypeError("GenericZeroMatrix does not have a specified shape")

    @property
    def shape(self):
        raise TypeError("GenericZeroMatrix does not have a specified shape")

    # Avoid Matrix.__eq__ which might call .shape
    def __eq__(self, other):
        return isinstance(other, GenericZeroMatrix)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return super().__hash__()



class Identity(MatrixExpr):
    """The Matrix Identity I - multiplicative identity

    Examples
    ========

    >>> from sympy.matrices import Identity, MatrixSymbol
    >>> A = MatrixSymbol('A', 3, 5)
    >>> I = Identity(3)
    >>> I*A
    A
    """

    is_Identity = True

    def __new__(cls, n):
        n = _sympify(n)
        cls._check_dim(n)

        return super().__new__(cls, n)

    @property
    def rows(self):
        return self.args[0]

    @property
    def cols(self):
        return self.args[0]

    @property
    def shape(self):
        return (self.args[0], self.args[0])

    @property
    def is_square(self):
        return True

    def _eval_transpose(self):
        return self

    def _eval_trace(self):
        return self.rows

    def _eval_inverse(self):
        return self

    def conjugate(self):
        return self

    def _entry(self, i, j, **kwargs):
        """
        Generates an identity matrix or a Kronecker delta matrix.
        
        Parameters
        ----------
        i : int
        The row index.
        j : int
        The column index.
        **kwargs : dict
        Additional keyword arguments.
        
        Returns
        -------
        out : Expr
        The output expression, which is 1 if i equals j, 0 if i does not equal j, or a Kronecker delta if i and j are within the specified range.
        
        Notes
        -----
        - If i equals j, the
        """

        eq = Eq(i, j)
        if eq is S.true:
            return S.One
        elif eq is S.false:
            return S.Zero
        return KroneckerDelta(i, j, (0, self.cols-1))

    def _eval_determinant(self):
        return S.One

    def _eval_power(self, exp):
        return self


class GenericIdentity(Identity):
    """
    An identity matrix without a specified shape

    This exists primarily so MatMul() with no arguments can return something
    meaningful.
    """
    def __new__(cls):
        # super(Identity, cls) instead of super(GenericIdentity, cls) because
        # Identity.__new__ doesn't have the same signature
        return super(Identity, cls).__new__(cls)

    @property
    def rows(self):
        raise TypeError("GenericIdentity does not have a specified shape")

    @property
    def cols(self):
        raise TypeError("GenericIdentity does not have a specified shape")

    @property
    def shape(self):
        raise TypeError("GenericIdentity does not have a specified shape")

    # Avoid Matrix.__eq__ which might call .shape
    def __eq__(self, other):
        return isinstance(other, GenericIdentity)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return super().__hash__()


class OneMatrix(MatrixExpr):
    """
    Matrix whose all entries are ones.
    """
    def __new__(cls, m, n, evaluate=False):
        m, n = _sympify(m), _sympify(n)
        cls._check_dim(m)
        cls._check_dim(n)

        if evaluate:
            condition = Eq(m, 1) & Eq(n, 1)
            if condition == True:
                return Identity(1)

        obj = super().__new__(cls, m, n)
        return obj

    @property
    def shape(self):
        return self._args

    @property
    def is_Identity(self):
        return self._is_1x1() == True

    def as_explicit(self):
        from sympy import ImmutableDenseMatrix
        return ImmutableDenseMatrix.ones(*self.shape)

    def doit(self, **hints):
        """
        doit(self, **hints)
        
        Evaluate the function with the given arguments.
        
        Parameters:
        - hints (dict): A dictionary of hints that can include a 'deep' key to control whether the arguments should be recursively evaluated. If 'deep' is True (default), each argument is evaluated using the doit method.
        
        Returns:
        - The result of the function evaluation with the evaluated arguments.
        
        This method is used to recursively evaluate the function and its arguments, ensuring that all components are in their evaluated form before performing
        """

        args = self.args
        if hints.get('deep', True):
            args = [a.doit(**hints) for a in args]
        return self.func(*args, evaluate=True)

    def _eval_power(self, exp):
        """
        Evaluate the power of a matrix.
        
        This function computes the power of a matrix. It handles special cases for exponent values of -1, 0, and 1. For a 1x1 matrix, it returns an Identity matrix of size 1. If the exponent is negative, it raises a NonInvertibleMatrixError. If the exponent is an integer, it returns the matrix raised to the power of the exponent minus one, multiplied by the identity matrix of the same size. Otherwise
        """

        # exp = -1, 0, 1 are already handled at this stage
        if self._is_1x1() == True:
            return Identity(1)
        if (exp < 0) == True:
            raise NonInvertibleMatrixError("Matrix det == 0; not invertible")
        if ask(Q.integer(exp)):
            return self.shape[0] ** (exp - 1) * OneMatrix(*self.shape)
        return super()._eval_power(exp)

    def _eval_transpose(self):
        return OneMatrix(self.cols, self.rows)

    def _eval_trace(self):
        return S.One*self.rows

    def _is_1x1(self):
        """Returns true if the matrix is known to be 1x1"""
        shape = self.shape
        return Eq(shape[0], 1) & Eq(shape[1], 1)

    def _eval_determinant(self):
        condition = self._is_1x1()
        if condition == True:
            return S.One
        elif condition == False:
            return S.Zero
        else:
            from sympy import Determinant
            return Determinant(self)

    def _eval_inverse(self):
        condition = self._is_1x1()
        if condition == True:
            return Identity(1)
        elif condition == False:
            raise NonInvertibleMatrixError("Matrix det == 0; not invertible.")
        else:
            from .inverse import Inverse
            return Inverse(self)

    def conjugate(self):
        return self

    def _entry(self, i, j, **kwargs):
        return S.One
