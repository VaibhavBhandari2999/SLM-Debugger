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
        """
        This function is a special method used for object creation in Python. It is the `__new__` method for the `ZeroMatrix` class, which is a subclass of `GenericZeroMatrix`.
        
        Parameters:
        - cls: The class itself, which is used to create a new instance of the class.
        
        Returns:
        - A new instance of the `ZeroMatrix` class. The method delegates the creation to the superclass's `__new__` method, ensuring that the object is properly initialized.
        """

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
        """
        Create a new Matrix object with dimensions m x n.
        
        Parameters:
        m (int or sympy expression): The number of rows in the matrix.
        n (int or sympy expression): The number of columns in the matrix.
        evaluate (bool, optional): If True, the function will evaluate the matrix to a specific case. Defaults to False.
        
        Returns:
        Matrix: A new Matrix object with the specified dimensions. If evaluate is True and both m and n are 1, returns
        """

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
        args = self.args
        if hints.get('deep', True):
            args = [a.doit(**hints) for a in args]
        return self.func(*args, evaluate=True)

    def _eval_power(self, exp):
        """
        Evaluate the power of a matrix.
        
        This function calculates the power of a matrix. It handles special cases for exponents -1, 0, and 1. For a 1x1 matrix, it returns an identity matrix. If the exponent is negative, it raises a NonInvertibleMatrixError if the matrix is not invertible. For integer exponents, it returns the matrix raised to the power of the exponent. For non-integer exponents, it delegates to the superclass method
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
        """
        Evaluate the determinant of a matrix.
        
        This function calculates the determinant of a matrix. If the matrix is 1x1,
        it returns 1. If the matrix is not valid for determinant calculation, it returns 0.
        For matrices larger than 1x1, it uses the `Determinant` class from `sympy` to compute the determinant.
        
        Parameters:
        self (Matrix): The matrix for which the determinant is to be calculated.
        
        Returns:
        sympy.core.num
        """

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
