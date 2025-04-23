import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sympy.matrices.densetools import eye
    from sympy.matrices.densearith import add, sub, mulmatmat, mulmatscaler
from sympy import ZZ


def test_add():
    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = [[ZZ(5), ZZ(4), ZZ(9)], [ZZ(3), ZZ(7), ZZ(1)], [ZZ(12), ZZ(13), ZZ(14)]]
    c = [[ZZ(12)], [ZZ(17)], [ZZ(21)]]
    d = [[ZZ(3)], [ZZ(4)], [ZZ(5)]]
    e = [[ZZ(12), ZZ(78)], [ZZ(56), ZZ(79)]]
    f = [[ZZ.zero, ZZ.zero], [ZZ.zero, ZZ.zero]]

    assert add(a, b, ZZ) == [[ZZ(8), ZZ(11), ZZ(13)], [ZZ(5), ZZ(11), ZZ(6)], [ZZ(18), ZZ(15), ZZ(17)]]
    assert add(c, d, ZZ) == [[ZZ(15)], [ZZ(21)], [ZZ(26)]]
    assert add(e, f, ZZ) == e


def test_sub():
    """
    Subtracts two matrices or vectors, or subtracts a scalar from each element of a matrix or vector.
    
    Parameters:
    a (list of lists or list): The first matrix or vector.
    b (list of lists or list): The second matrix or vector to be subtracted from the first.
    field (class): The field over which the subtraction is performed (e.g., ZZ for integers).
    
    Returns:
    list: The resulting matrix or vector after subtraction.
    
    Examples:
    >>> test_sub
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = [[ZZ(5), ZZ(4), ZZ(9)], [ZZ(3), ZZ(7), ZZ(1)], [ZZ(12), ZZ(13), ZZ(14)]]
    c = [[ZZ(12)], [ZZ(17)], [ZZ(21)]]
    d = [[ZZ(3)], [ZZ(4)], [ZZ(5)]]
    e = [[ZZ(12), ZZ(78)], [ZZ(56), ZZ(79)]]
    f = [[ZZ.zero, ZZ.zero], [ZZ.zero, ZZ.zero]]

    assert sub(a, b, ZZ) == [[ZZ(-2), ZZ(3), ZZ(-5)], [ZZ(-1), ZZ(-3), ZZ(4)], [ZZ(-6), ZZ(-11), ZZ(-11)]]
    assert sub(c, d, ZZ) == [[ZZ(9)], [ZZ(13)], [ZZ(16)]]
    assert sub(e, f, ZZ) == e


def test_mulmatmat():
    """
    Multiply two matrices over the integers.
    
    Parameters:
    a (list of lists): The first matrix.
    b (list of lists): The second matrix.
    c (optional, Matrix): The identity matrix for the operation.
    
    Returns:
    list of lists: The resulting matrix after multiplication.
    
    Examples:
    >>> test_mulmatmat()
    True
    """

    a = [[ZZ(3), ZZ(4)], [ZZ(5), ZZ(6)]]
    b = [[ZZ(1), ZZ(2)], [ZZ(7), ZZ(8)]]
    c = eye(2, ZZ)
    d = [[ZZ(6)], [ZZ(7)]]

    assert mulmatmat(a, b, ZZ) == [[ZZ(31), ZZ(38)], [ZZ(47), ZZ(58)]]
    assert mulmatmat(b, d, ZZ) == [[ZZ(20)], [ZZ(98)]]



def test_mulmatscaler():
    a = eye(3, ZZ)
    b = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]

    assert mulmatscaler(a, ZZ(4), ZZ) == [[ZZ(4), ZZ(0), ZZ(0)], [ZZ(0), ZZ(4), ZZ(0)], [ZZ(0), ZZ(0), ZZ(4)]]
    assert mulmatscaler(b, ZZ(1), ZZ) == [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
