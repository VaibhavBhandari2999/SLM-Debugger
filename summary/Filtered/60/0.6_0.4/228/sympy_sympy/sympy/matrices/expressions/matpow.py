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
        
        Parameters
        ----------
        base : Matrix
        The base matrix which should be a Matrix object.
        exp : int or sympy expression
        The exponent which can be an integer or a sympy expression.
        
        Returns
        -------
        MatrixPower
        A MatrixPower object representing the matrix raised to the given power.
        
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
        
        Parameters
        ----------
        deep : bool, optional
        If True (default), recursively evaluate the base matrix and exponent.
        If False, use the provided base and exponent matrices as-is.
        kwargs : dict
        Additional keyword arguments that may be required for evaluation.
        
        Returns
        -------
        MatrixBase
        The evaluated matrix power expression.
        
        Notes
        -----
        - If the exponent is zero and the base matrix is square, the identity matrix of the same
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
