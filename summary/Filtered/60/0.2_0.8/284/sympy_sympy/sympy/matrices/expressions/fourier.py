from sympy.core.sympify import _sympify
from sympy.matrices.expressions import MatrixExpr
from sympy import S, I, sqrt, exp

class DFT(MatrixExpr):
    """ Discrete Fourier Transform """
    def __new__(cls, n):
        """
        Construct a new matrix object with the specified dimension.
        
        Parameters:
        n (int or sympy expression): The dimension of the matrix.
        
        Returns:
        Matrix: A matrix object with the specified dimension.
        
        Notes:
        - The input `n` is first converted to a sympy expression using `_sympify`.
        - The dimension `n` is validated using the `_check_dim` method.
        - A new matrix object is created using the superclass's `__new__` method and returned
        """

        n = _sympify(n)
        cls._check_dim(n)

        obj = super().__new__(cls, n)
        return obj

    n = property(lambda self: self.args[0])  # type: ignore
    shape = property(lambda self: (self.n, self.n))  # type: ignore

    def _entry(self, i, j, **kwargs):
        w = exp(-2*S.Pi*I/self.n)
        return w**(i*j) / sqrt(self.n)

    def _eval_inverse(self):
        return IDFT(self.n)

class IDFT(DFT):
    """ Inverse Discrete Fourier Transform """
    def _entry(self, i, j, **kwargs):
        w = exp(-2*S.Pi*I/self.n)
        return w**(-i*j) / sqrt(self.n)

    def _eval_inverse(self):
        return DFT(self.n)
