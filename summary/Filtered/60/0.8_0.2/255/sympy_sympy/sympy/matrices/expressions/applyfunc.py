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
        Creates a new MatrixExpr object.
        
        This method is a special constructor for the MatrixExpr class. It takes a function and an expression as input and returns a new MatrixExpr object. The function and expression are stored as attributes of the new object.
        
        Parameters:
        cls (type): The MatrixExpr class.
        function (callable): A function to be associated with the MatrixExpr object.
        expr (object): An expression to be associated with the MatrixExpr object.
        
        Returns:
        MatrixExpr: A
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
        """
        Apply a mathematical function to each element of a matrix or expression.
        
        Parameters:
        deep (bool, optional): If True, apply the function to all nested expressions as well. Default is True.
        kwargs: Additional keyword arguments that are passed to the function when applied to each element.
        
        Returns:
        MatrixBase or original expression: If the input is a matrix, a new matrix with the function applied to each element is returned. If the input is not a matrix, the original expression is returned.
        """

        deep = kwargs.get("deep", True)
        expr = self.expr
        if deep:
            expr = expr.doit(**kwargs)
        if isinstance(expr, MatrixBase):
            return expr.applyfunc(self.function)
        else:
            return self
