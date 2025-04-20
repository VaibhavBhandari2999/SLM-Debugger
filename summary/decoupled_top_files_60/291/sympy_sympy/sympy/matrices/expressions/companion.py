from sympy.core.singleton import S
from sympy.core.sympify import _sympify
from sympy.polys.polytools import Poly

from .matexpr import MatrixExpr


class CompanionMatrix(MatrixExpr):
    """A symbolic companion matrix of a polynomial.

    Examples
    ========

    >>> from sympy import Poly, Symbol, symbols
    >>> from sympy.matrices.expressions import CompanionMatrix
    >>> x = Symbol('x')
    >>> c0, c1, c2, c3, c4 = symbols('c0:5')
    >>> p = Poly(c0 + c1*x + c2*x**2 + c3*x**3 + c4*x**4 + x**5, x)
    >>> CompanionMatrix(p)
    CompanionMatrix(Poly(x**5 + c4*x**4 + c3*x**3 + c2*x**2 + c1*x + c0,
    x, domain='ZZ[c0,c1,c2,c3,c4]'))
    """
    def __new__(cls, poly):
        """
        Construct a new univariate monic polynomial of degree at least 1.
        
        Parameters:
        - poly (Poly): The input polynomial that must be a Poly instance, monic, univariate, and of degree at least 1.
        
        Returns:
        - Poly: A new instance of the Poly class representing the input polynomial.
        
        Raises:
        - ValueError: If the input is not a Poly instance, not monic, not univariate, or has a degree less than 1.
        """

        poly = _sympify(poly)
        if not isinstance(poly, Poly):
            raise ValueError("{} must be a Poly instance.".format(poly))
        if not poly.is_monic:
            raise ValueError("{} must be a monic polynomial.".format(poly))
        if not poly.is_univariate:
            raise ValueError(
                "{} must be a univariate polynomial.".format(poly))
        if not poly.degree() >= 1:
            raise ValueError(
                "{} must have degree not less than 1.".format(poly))

        return super().__new__(cls, poly)


    @property
    def shape(self):
        poly = self.args[0]
        size = poly.degree()
        return size, size


    def _entry(self, i, j):
        """
        Generate the entry of the matrix used in the computation of the resultant.
        
        This function computes the coefficients for the matrix used in the resultant computation, which is a fundamental tool in elimination theory and polynomial algebra.
        
        Parameters:
        i (int): The row index of the matrix entry.
        j (int): The column index of the matrix entry.
        
        Returns:
        sympy.core.numbers.One or sympy.core.numbers.Zero:
        - If `i == j + 1`, returns `1
        """

        if j == self.cols - 1:
            return -self.args[0].all_coeffs()[-1 - i]
        elif i == j + 1:
            return S.One
        return S.Zero


    def as_explicit(self):
        from sympy.matrices.immutable import ImmutableDenseMatrix
        return ImmutableDenseMatrix.companion(self.args[0])
