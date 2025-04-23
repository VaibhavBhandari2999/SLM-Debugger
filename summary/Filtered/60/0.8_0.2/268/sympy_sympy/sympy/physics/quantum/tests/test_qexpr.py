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
    q1 = QExpr(x)
    q2 = QExpr(y)
    assert q1.is_commutative is False
    assert q2.is_commutative is False
    assert q1*q2 != q2*q1

    q = QExpr._new_rawargs(0, 1, HilbertSpace())
    assert q.is_commutative is False

def test_qexpr_commutative_free_symbols():
    """
    Tests the commutative property of free symbols in a Quantum Expression (QExpr).
    
    This function checks if the free symbols in a Quantum Expression (QExpr) are non-commutative.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> q1 = QExpr(x)
    >>> test_qexpr_commutative_free_symbols()
    # This will assert that the free symbol in q1 is non-commutative.
    
    >>> q2 = QExpr('q2')
    """

    q1 = QExpr(x)
    assert q1.free_symbols.pop().is_commutative is False

    q2 = QExpr('q2')
    assert q2.free_symbols.pop().is_commutative is False

def test_qexpr_subs():
    q1 = QExpr(x, y)
    assert q1.subs(x, y) == QExpr(y, y)
    assert q1.subs({x: 1, y: 2}) == QExpr(1, 2)


def test_qsympify():
    """
    Sympify a sequence of values.
    
    This function takes a sequence of values and converts them into a sympy-compatible format. It supports nested lists and tuples, and can handle a mix of integers and nested structures.
    
    Parameters:
    sequence (list or tuple): The input sequence containing integers and/or nested lists/tuples.
    
    Returns:
    tuple: A tuple of sympified values, where nested lists and tuples are also converted to their sympy equivalents.
    
    Examples:
    >>> test_qsympify()
    """

    assert _qsympify_sequence([[1, 2], [1, 3]]) == (Tuple(1, 2), Tuple(1, 3))
    assert _qsympify_sequence(([1, 2, [3, 4, [2, ]], 1], 3)) == \
        (Tuple(1, 2, Tuple(3, 4, Tuple(2,)), 1), 3)
    assert _qsympify_sequence((1,)) == (1,)
