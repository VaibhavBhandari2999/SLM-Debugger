from sympy.matrices.expressions import MatrixExpr
from sympy import MatrixBase


class ElementwiseApplyFunction(MatrixExpr):
    r"""
    Apply function to a matrix elementwise without evaluating.

    Examples
    ========

    >>> from sympy.matrices.expressions import MatrixSymbol
    >>> from sympy.matrices.expressions.applyfunc import ElementwiseApplyFunction
    >>> from sympy import exp
    >>> X = MatrixSymbol("X", 3, 3)
    >>> X.applyfunc(exp)
    ElementwiseApplyFunction(exp, X)

    >>> from sympy import eye
    >>> expr = ElementwiseApplyFunction(exp, eye(3))
    >>> expr
    ElementwiseApplyFunction(exp, Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]]))
    >>> expr.doit()
    Matrix([
    [E, 1, 1],
    [1, E, 1],
    [1, 1, E]])

    Notice the difference with the real mathematical functions:

    >>> exp(eye(3))
    Matrix([
    [E, 0, 0],
    [0, E, 0],
    [0, 0, E]])
    """

    def __new__(cls, function, expr):
        """
        Create a new MatrixExpr object.
        
        This method is used to instantiate a new MatrixExpr object with a given function and expression.
        
        Parameters:
        function (callable): The function associated with the MatrixExpr.
        expr (object): The expression associated with the MatrixExpr.
        
        Returns:
        MatrixExpr: A new instance of the MatrixExpr class.
        
        Attributes:
        _function (callable): The function associated with the MatrixExpr.
        _expr (object): The expression associated with the MatrixExpr.
        """

        obj = MatrixExpr.__new__(cls, function, expr)
        obj._function = function
        obj._expr = expr
        return obj

    @property
    def function(self):
        return self._function

    @property
    def expr(self):
        return self._expr

    @property
    def shape(self):
        return self.expr.shape

    def doit(self, **kwargs):
        deep = kwargs.get("deep", True)
        expr = self.expr
        if deep:
            expr = expr.doit(**kwargs)
        if isinstance(expr, MatrixBase):
            return expr.applyfunc(self.function)
        else:
            return self
