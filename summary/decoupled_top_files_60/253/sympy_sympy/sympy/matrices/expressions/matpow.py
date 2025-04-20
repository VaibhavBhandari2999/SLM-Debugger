from __future__ import print_function, division

from .matexpr import MatrixExpr, ShapeError, Identity, ZeroMatrix
from .transpose import Transpose
from sympy.core.sympify import _sympify
from sympy.core.compatibility import range
from sympy.matrices import MatrixBase
from sympy.core import S, Basic


class MatPow(MatrixExpr):

    def __new__(cls, base, exp):
        """
        Create a matrix power.
        
        This class represents a matrix raised to a power and is used to
        handle the operation symbolically. The actual computation is
        performed when needed.
        
        Parameters:
        - base (Matrix): The base matrix which must be a Matrix object.
        - exp (Expression): The exponent which can be any SymPy expression.
        
        Returns:
        - MatPow: A symbolic representation of the matrix raised to the given power.
        
        Raises:
        - TypeError: If the base is not a Matrix object.
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

    def _entry(self, i, j, **kwargs):
        from sympy.matrices.expressions import MatMul
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
                # Leave the expression unevaluated:
                from sympy.matrices.expressions.matexpr import MatrixElement
                return MatrixElement(self, i, j)
        return A._entry(i, j)

    def doit(self, **kwargs):
        """
        Evaluate the matrix power expression.
        
        This function evaluates the matrix power expression, handling various cases
        such as deep evaluation, identity and zero matrices, and scalar exponents.
        It also supports special cases like the inverse of a matrix and the identity
        matrix raised to any power.
        
        Parameters:
        self (MatPow): The matrix power expression to be evaluated.
        **kwargs: Additional keyword arguments, including 'deep' to control whether
        the evaluation should be deep (default is True).
        
        Returns:
        """

        from sympy.matrices.expressions import Inverse
        deep = kwargs.get('deep', True)
        if deep:
            args = [arg.doit(**kwargs) for arg in self.args]
        else:
            args = self.args

        base, exp = args
        # combine all powers, e.g. (A**2)**3 = A**6
        while isinstance(base, MatPow):
            exp = exp*base.args[1]
            base = base.args[0]

        if exp.is_zero and base.is_square:
            if isinstance(base, MatrixBase):
                return base.func(Identity(base.shape[0]))
            return Identity(base.shape[0])
        elif isinstance(base, ZeroMatrix) and exp.is_negative:
            raise ValueError("Matrix determinant is 0, not invertible.")
        elif isinstance(base, (Identity, ZeroMatrix)):
            return base
        elif isinstance(base, MatrixBase) and exp.is_number:
            if exp is S.One:
                return base
            return base**exp
        # Note: just evaluate cases we know, return unevaluated on others.
        # E.g., MatrixSymbol('x', n, m) to power 0 is not an error.
        elif exp is S(-1) and base.is_square:
            return Inverse(base).doit(**kwargs)
        elif exp is S.One:
            return base
        return MatPow(base, exp)

    def _eval_transpose(self):
        base, exp = self.args
        return MatPow(base.T, exp)
