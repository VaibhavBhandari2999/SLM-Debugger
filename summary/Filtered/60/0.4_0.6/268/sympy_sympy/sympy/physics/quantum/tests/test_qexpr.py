from sympy import Symbol, Integer
from sympy.physics.quantum.qexpr import QExpr, _qsympify_sequence
from sympy.physics.quantum.hilbert import HilbertSpace
from sympy.core.containers import Tuple

x = Symbol('x')
y = Symbol('y')


def test_qexpr_new():
    q = QExpr(0)
    assert q.label == (0,)
    assert q.hilbert_space == HilbertSpace()
    assert q.is_commutative is False

    q = QExpr(0, 1)
    assert q.label == (Integer(0), Integer(1))

    q = QExpr._new_rawargs(HilbertSpace(), Integer(0), Integer(1))
    assert q.label == (Integer(0), Integer(1))
    assert q.hilbert_space == HilbertSpace()


def test_qexpr_commutative():
    """
    Test the commutativity of quantum expressions (QExpr).
    
    This function checks the commutativity properties of quantum expressions involving different symbols and a raw QExpr.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `q1` and `q2` are QExpr instances with symbols `x` and `y` respectively.
    - Both `q1` and `q2` are non-commutative.
    - The product of `q1` and `
    """

    q1 = QExpr(x)
    q2 = QExpr(y)
    assert q1.is_commutative is False
    assert q2.is_commutative is False
    assert q1*q2 != q2*q1

    q = QExpr._new_rawargs(0, 1, HilbertSpace())
    assert q.is_commutative is False

def test_qexpr_commutative_free_symbols():
    q1 = QExpr(x)
    assert q1.free_symbols.pop().is_commutative is False

    q2 = QExpr('q2')
    assert q2.free_symbols.pop().is_commutative is False

def test_qexpr_subs():
    """
    Substitute variables in a QExpr.
    
    This function substitutes variables in a QExpr with specified values.
    
    Parameters:
    q1 (QExpr): The QExpr to be modified.
    x (Any): The value to substitute for the variable x.
    y (Any): The value to substitute for the variable y.
    kwargs (dict, optional): A dictionary of variable-value pairs for substitution.
    
    Returns:
    QExpr: The modified QExpr after substitution.
    
    Examples:
    >>> q1 =
    """

    q1 = QExpr(x, y)
    assert q1.subs(x, y) == QExpr(y, y)
    assert q1.subs({x: 1, y: 2}) == QExpr(1, 2)


def test_qsympify():
    assert _qsympify_sequence([[1, 2], [1, 3]]) == (Tuple(1, 2), Tuple(1, 3))
    assert _qsympify_sequence(([1, 2, [3, 4, [2, ]], 1], 3)) == \
        (Tuple(1, 2, Tuple(3, 4, Tuple(2,)), 1), 3)
    assert _qsympify_sequence((1,)) == (1,)
