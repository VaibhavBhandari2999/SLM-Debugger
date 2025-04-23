from sympy import Symbol, Integer
from sympy.physics.quantum.qexpr import QExpr, _qsympify_sequence
from sympy.physics.quantum.hilbert import HilbertSpace
from sympy.core.containers import Tuple

x = Symbol('x')
y = Symbol('y')


def test_qexpr_new():
    """
    Create a new QExpr instance.
    
    This function initializes a QExpr object with specified labels and an optional Hilbert space.
    
    Parameters:
    label (tuple): The label for the QExpr, typically a tuple of integers.
    hilbert_space (HilbertSpace, optional): The Hilbert space associated with the QExpr. Defaults to HilbertSpace().
    
    Returns:
    QExpr: A new QExpr instance with the specified label and Hilbert space.
    """

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
    
    This function substitutes variables in a QExpr object with specified values.
    
    Parameters:
    q1 (QExpr): The QExpr object in which variables are to be substituted.
    x (int): The value to substitute for variable x.
    y (int): The value to substitute for variable y.
    args (tuple, optional): A tuple of values to substitute for the variables in the order they appear in the QExpr.
    kwargs (dict, optional
    """

    q1 = QExpr(x, y)
    assert q1.subs(x, y) == QExpr(y, y)
    assert q1.subs({x: 1, y: 2}) == QExpr(1, 2)


def test_qsympify():
    assert _qsympify_sequence([[1, 2], [1, 3]]) == (Tuple(1, 2), Tuple(1, 3))
    assert _qsympify_sequence(([1, 2, [3, 4, [2, ]], 1], 3)) == \
        (Tuple(1, 2, Tuple(3, 4, Tuple(2,)), 1), 3)
    assert _qsympify_sequence((1,)) == (1,)
