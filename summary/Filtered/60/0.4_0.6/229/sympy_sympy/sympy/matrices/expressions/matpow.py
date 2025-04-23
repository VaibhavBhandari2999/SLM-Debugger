from __future__ import print_function, division

from .matexpr import MatrixExpr, ShapeError, Identity, ZeroMatrix
from sympy.core.sympify import _sympify
from sympy.core.compatibility import range
from sympy.matrices import MatrixBase
from sympy.core import S


class MatPow(MatrixExpr):

    def __new__(cls, base, exp):
        """
        Create a matrix power.
        
        This class represents a matrix raised to a power and simplifies the expression
        when the matrix or exponent is a specific value.
        
        Parameters
        ----------
        base : Matrix
        The base matrix which must be a Matrix object.
        exp : Integer
        The exponent which must be an integer.
        
        Returns
        -------
        MatPow
        An instance of the MatPow class representing the matrix power.
        
        Raises
        ------
        TypeError
        If the base is not a Matrix object.
        """

        base = _sympify(base)
        if not base.is_Matrix:
            raise TypeError("Function parameter should be a matrix")
        exp = _sympify(exp)
        return super(MatPow, cls).__new__(cls, base, exp)

    @property
    def base(self):
        return self.args[0]

    @property
    def exp(self):
        return self.args[1]

    @property
    def shape(self):
        return self.base.shape

    def _entry(self, i, j):
        """
        Generate an entry in the matrix resulting from a matrix power.
        
        This function computes the (i, j)-th entry of the matrix resulting from
        raising a given matrix to a specified power. The matrix and the power are
        determined by the `doit` method of the matrix object.
        
        Parameters
        ----------
        i : int
        The row index of the entry to be computed.
        j : int
        The column index of the entry to be computed.
        
        Returns
        -------
        entry : sympy.mat
        """

        A = self.doit()
        if isinstance(A, MatPow):
            # We still have a MatPow, make an explicit MatMul out of it.
            if not A.base.is_square:
                raise ShapeError("Power of non-square matrix %s" % A.base)
            elif A.exp.is_Integer and A.exp.is_positive:
                A = MatMul(*[A.base for k in range(A.exp)])
            #elif A.exp.is_Integer and self.exp.is_negative:
            # Note: possible future improvement: in principle we can take
            # positive powers of the inverse, but carefully avoid recursion,
            # perhaps by adding `_entry` to Inverse (as it is our subclass).
            # T = A.base.as_explicit().inverse()
            # A = MatMul(*[T for k in range(-A.exp)])
            else:
                raise NotImplementedError(("(%d, %d) entry" % (int(i), int(j)))
                    + " of matrix power either not defined or not implemented")
        return A._entry(i, j)


    def doit(self, **kwargs):
        """
        doit(self, **kwargs)
        
        Evaluate the matrix power expression.
        
        Parameters:
        - deep (bool, optional): If True, evaluate the arguments of the matrix power expression. Default is True.
        - kwargs: Additional keyword arguments that may be required for evaluation.
        
        Returns:
        - The evaluated matrix power expression, or an unevaluated MatPow object if the expression cannot be simplified further.
        
        This function evaluates the matrix power expression based on the given parameters and additional keyword arguments. It handles various cases such as zero
        """

        deep = kwargs.get('deep', True)
        if deep:
            args = [arg.doit(**kwargs) for arg in self.args]
        else:
            args = self.args
        base = args[0]
        exp = args[1]
        if exp.is_zero and base.is_square:
            if isinstance(base, MatrixBase):
                return base.func(Identity(base.shape[0]))
            return Identity(base.shape[0])
        elif isinstance(base, ZeroMatrix) and exp.is_negative:
            raise ValueError("Matrix det == 0; not invertible.")
        elif isinstance(base, (Identity, ZeroMatrix)):
            return base
        elif isinstance(base, MatrixBase) and exp.is_number:
            if exp is S.One:
                return base
            return base**exp
        # Note: just evaluate cases we know, return unevaluated on others.
        # E.g., MatrixSymbol('x', n, m) to power 0 is not an error.
        elif exp is S.One:
            return base
        return MatPow(base, exp)


from .matmul import MatMul
