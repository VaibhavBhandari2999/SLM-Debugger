from __future__ import print_function, division

from sympy.core.sympify import _sympify
from sympy.matrices.expressions import MatrixExpr
from sympy import S, I, sqrt, exp

class DFT(MatrixExpr):
    """ Discrete Fourier Transform """
    def __new__(cls, n):
        """
        Construct a Discrete Fourier Transform (DFT) matrix of size n x n.
        
        Parameters:
        n (int): The size of the DFT matrix to construct. Must be a positive integer.
        
        Returns:
        DFT: A DFT object representing the n x n DFT matrix.
        
        Raises:
        ValueError: If n is not a positive integer.
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
