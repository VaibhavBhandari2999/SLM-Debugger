from __future__ import print_function, division

from sympy.core import Basic
from sympy.functions import adjoint, conjugate
from sympy.matrices.expressions.transpose import transpose
from sympy.matrices.expressions.matexpr import MatrixExpr


class Adjoint(MatrixExpr):
    """
    The Hermitian adjoint of a matrix expression.

    This is a symbolic object that simply stores its argument without
    evaluating it. To actually compute the adjoint, use the ``adjoint()``
    function.

    Examples
    ========

    >>> from sympy.matrices import MatrixSymbol, Adjoint
    >>> from sympy.functions import adjoint
    >>> A = MatrixSymbol('A', 3, 5)
    >>> B = MatrixSymbol('B', 5, 3)
    >>> Adjoint(A*B)
    Adjoint(A*B)
    >>> adjoint(A*B)
    Adjoint(B)*Adjoint(A)
    >>> adjoint(A*B) == Adjoint(A*B)
    False
    >>> adjoint(A*B) == Adjoint(A*B).doit()
    True
    """
    is_Adjoint = True

    def doit(self, **hints):
        """
        Performs the adjoint operation on the result of the 'arg' attribute's doit method.
        
        Parameters:
        arg (Basic): The argument on which the adjoint operation is to be performed.
        hints (dict, optional): Additional hints for the doit method. If 'deep' is True (default), the operation is applied recursively to nested Basic objects.
        
        Returns:
        adjoint(Basic): The adjoint of the result obtained by calling 'arg.doit(**hints)'.
        
        This method is
        """

        arg = self.arg
        if hints.get('deep', True) and isinstance(arg, Basic):
            return adjoint(arg.doit(**hints))
        else:
            return adjoint(self.arg)

    @property
    def arg(self):
        return self.args[0]

    @property
    def shape(self):
        return self.arg.shape[::-1]

    def _entry(self, i, j, **kwargs):
        return conjugate(self.arg._entry(j, i, **kwargs))

    def _eval_adjoint(self):
        return self.arg

    def _eval_conjugate(self):
        return transpose(self.arg)

    def _eval_trace(self):
        from sympy.matrices.expressions.trace import Trace
        return conjugate(Trace(self.arg))

    def _eval_transpose(self):
        return conjugate(self.arg)
