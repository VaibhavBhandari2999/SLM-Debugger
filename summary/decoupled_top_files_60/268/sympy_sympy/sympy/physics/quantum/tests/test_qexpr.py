from sympy import Symbol, Integer
from sympy.physics.quantum.qexpr import QExpr, _qsympify_sequence
from sympy.physics.quantum.hilbert import HilbertSpace
from sympy.core.containers import Tuple

x = Symbol('x')
y = Symbol('y')


def test_qexpr_new():
    """
    Create a new QExpr instance.
    
    This function initializes a QExpr object with the given arguments. It can either be called directly with the required arguments or used as a class method `_new_rawargs` to create a QExpr instance with a specified Hilbert space.
    
    Parameters:
    label (tuple): A tuple representing the label of the QExpr.
    hilbert_space (HilbertSpace, optional): The Hilbert space associated with the QExpr. If not provided, a default Hilbert
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
    """
    Test the commutative property of free symbols in a QExpr.
    
    This function checks the commutative property of free symbols in two different QExpr instances. The first QExpr instance is created with the symbol 'x', and the second is created with the string 'q2'. It asserts that the free symbols in both QExpr instances are not commutative.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The free symbol of the first QExpr instance created with 'x' is
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
    
    This function takes a sequence of values and converts them into a tuple of sympified values. It supports nested lists and tuples, converting each element to a sympified form.
    
    Parameters:
    sequence (list or tuple): The input sequence containing values to be sympified.
    
    Returns:
    tuple: A tuple of sympified values from the input sequence.
    
    Examples:
    >>> test_qsympify()
    (Tuple(1, 2), Tuple(1,
    """

    assert _qsympify_sequence([[1, 2], [1, 3]]) == (Tuple(1, 2), Tuple(1, 3))
    assert _qsympify_sequence(([1, 2, [3, 4, [2, ]], 1], 3)) == \
        (Tuple(1, 2, Tuple(3, 4, Tuple(2,)), 1), 3)
    assert _qsympify_sequence((1,)) == (1,)
