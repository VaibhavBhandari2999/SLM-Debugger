from sympy.core.sympify import _sympify
from sympy.matrices.expressions import MatrixExpr
from sympy import S, I, sqrt, exp

class DFT(MatrixExpr):
    """ Discrete Fourier Transform """
    def __new__(cls, n):
        """
        Create a new instance of the class with the specified dimension `n`.
        
        Parameters:
        n (int): The dimension of the object to be created.
        
        Returns:
        object: A new instance of the class with the specified dimension.
        
        Notes:
        - The input `n` is first converted to a SymPy object using `_sympify`.
        - The `_check_dim` method is called to validate the dimension `n`.
        - The superclass's `__new__` method is called to
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
