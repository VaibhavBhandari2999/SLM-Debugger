from __future__ import print_function, division

from sympy.core import Basic
from sympy.core.sympify import _sympify
from sympy.matrices.expressions.transpose import transpose
from sympy.matrices.expressions.matexpr import MatrixExpr


class DotProduct(MatrixExpr):
    """
    Dot product of vector matrices

    The input should be two 1 x n or n x 1 matrices. The output represents the
    scalar dotproduct.

    This is similar to using MatrixElement and MatMul, except DotProduct does
    not require that one vector to be a row vector and the other vector to be
    a column vector.

    >>> from sympy import MatrixSymbol, DotProduct
    >>> A = MatrixSymbol('A', 1, 3)
    >>> B = MatrixSymbol('B', 1, 3)
    >>> DotProduct(A, B)
    DotProduct(A, B)
    >>> DotProduct(A, B).doit()
    A[0, 0]*B[0, 0] + A[0, 1]*B[0, 1] + A[0, 2]*B[0, 2]
    """

    def __new__(cls, arg1, arg2):
        """
        Create a DotProduct object from two matrices.
        
        This function is used to create a DotProduct object representing the dot product of two matrices. The matrices must be vectors (i.e., one-dimensional matrices) and of the same length. The function checks that both inputs are matrices and that they are vectors (i.e., have a shape of (n, 1) or (1, n)).
        
        Parameters:
        arg1 (Matrix): The first matrix, which must be a vector.
        arg
        """

        arg1, arg2 = _sympify((arg1, arg2))

        if not arg1.is_Matrix:
            raise TypeError("Argument 1 of DotProduct is not a matrix")
        if not arg2.is_Matrix:
            raise TypeError("Argument 2 of DotProduct is not a matrix")
        if not (1 in arg1.shape):
            raise TypeError("Argument 1 of DotProduct is not a vector")
        if not (1 in arg2.shape):
            raise TypeError("Argument 2 of DotProduct is not a vector")

        if set(arg1.shape) != set(arg2.shape):
            raise TypeError("DotProduct arguments are not the same length")

        return Basic.__new__(cls, arg1, arg2)

    def doit(self, expand=False):
        """
        Generate a matrix multiplication or element-wise multiplication based on the shapes of the input arguments.
        
        Parameters:
        self (object): The object instance containing the arguments for the operation.
        expand (bool, optional): If True, expands the dimensions of the input arguments to perform broadcasting. Default is False.
        
        Returns:
        numpy.ndarray: The result of the multiplication operation, either matrix multiplication or element-wise multiplication, depending on the shapes of the input arguments.
        
        Notes:
        - If the shapes of the input arguments
        """

        if self.args[0].shape == self.args[1].shape:
            if self.args[0].shape[0] == 1:
                mul = self.args[0]*transpose(self.args[1])
            else:
                mul = transpose(self.args[0])*self.args[1]
        else:
            if self.args[0].shape[0] == 1:
                mul = self.args[0]*self.args[1]
            else:
                mul = transpose(self.args[0])*transpose(self.args[1])

        return mul[0]
