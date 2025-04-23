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
        Constructs a new instance of the class from a given polynomial.
        
        Parameters:
        poly (Poly): A polynomial instance that must be monic, univariate, and have a degree not less than 1.
        
        Returns:
        object: A new instance of the class.
        
        Raises:
        ValueError: If the input polynomial is not monic, not univariate, or has a degree less than 1.
        TypeError: If the input is not a Poly instance.
        
        This method ensures that the input polynomial
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
        """
        shape(self) -> tuple
        
        This method returns the dimensions of the polynomial shape.
        
        Parameters:
        self (Poly): The Poly object representing the polynomial.
        
        Returns:
        tuple: A tuple containing the degree of the polynomial in both x and y dimensions.
        
        Note:
        The polynomial is assumed to be a square matrix (i.e., the degree in x and y dimensions is the same).
        """

        poly = self.args[0]
        size = poly.degree()
        return size, size


    def _entry(self, i, j):
        if j == self.cols - 1:
            return -self.args[0].all_coeffs()[-1 - i]
        elif i == j + 1:
            return S.One
        return S.Zero


    def as_explicit(self):
        from sympy.matrices.immutable import ImmutableDenseMatrix
        return ImmutableDenseMatrix.companion(self.args[0])
