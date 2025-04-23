from __future__ import print_function, division

from sympy.core.sympify import _sympify
from sympy.matrices.expressions import MatrixExpr
from sympy import S, I, sqrt, exp

class DFT(MatrixExpr):
    """ Discrete Fourier Transform """
    def __new__(cls, n):
        """
        Create a Discrete Fourier Transform (DFT) object.
        
        Parameters:
        n (int): The dimension of the DFT, which must be a positive integer.
        
        Returns:
        DFT: A DFT object representing the specified dimension.
        
        This method initializes a DFT object by first converting the input `n` to a SymPy object and then checking its dimension. It then creates a new instance of the DFT class using the superclass's `__new__` method and returns the newly created
        """

        n = _sympify(n)
        cls._check_dim(n)

        obj = super(DFT, cls).__new__(cls, n)
        return obj

    n = property(lambda self: self.args[0])
    shape = property(lambda self: (self.n, self.n))

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
