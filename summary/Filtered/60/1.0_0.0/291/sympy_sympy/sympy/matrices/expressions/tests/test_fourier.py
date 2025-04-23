from sympy.assumptions.ask import (Q, ask)
from sympy.core.numbers import (I, Rational)
from sympy.core.singleton import S
from sympy.functions.elementary.complexes import Abs
from sympy.functions.elementary.exponential import exp
from sympy.functions.elementary.miscellaneous import sqrt
from sympy.simplify.simplify import simplify
from sympy.core.symbol import symbols
from sympy.matrices.expressions.fourier import DFT, IDFT
from sympy.matrices import det, Matrix, Identity
from sympy.testing.pytest import raises


def test_dft_creation():
    """
    Test the creation of a Discrete Fourier Transform (DFT) object.
    
    Parameters:
    - n (int or Symbol): The size of the DFT or a symbolic variable representing the index.
    
    Returns:
    - DFT object: A DFT object is returned if `n` is a valid integer.
    - ValueError: Raised if `n` is a negative integer, a floating-point number, or a symbolic variable that is not non-negative.
    
    Examples:
    - DFT(2) should return a valid
    """

    assert DFT(2)
    assert DFT(0)
    raises(ValueError, lambda: DFT(-1))
    raises(ValueError, lambda: DFT(2.0))
    raises(ValueError, lambda: DFT(2 + 1j))

    n = symbols('n')
    assert DFT(n)
    n = symbols('n', integer=False)
    raises(ValueError, lambda: DFT(n))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: DFT(n))


def test_dft():
    n, i, j = symbols('n i j')
    assert DFT(4).shape == (4, 4)
    assert ask(Q.unitary(DFT(4)))
    assert Abs(simplify(det(Matrix(DFT(4))))) == 1
    assert DFT(n)*IDFT(n) == Identity(n)
    assert DFT(n)[i, j] == exp(-2*S.Pi*I/n)**(i*j) / sqrt(n)


def test_dft2():
    assert DFT(1).as_explicit() == Matrix([[1]])
    assert DFT(2).as_explicit() == 1/sqrt(2)*Matrix([[1,1],[1,-1]])
    assert DFT(4).as_explicit() == Matrix([[S.Half,  S.Half,  S.Half, S.Half],
                                           [S.Half, -I/2, Rational(-1,2),  I/2],
                                           [S.Half, Rational(-1,2),  S.Half, Rational(-1,2)],
                                           [S.Half,  I/2, Rational(-1,2), -I/2]])
Rational(-1,2), -I/2]])
