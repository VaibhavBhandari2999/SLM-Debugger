from sympy.core.compatibility import range
from sympy.ntheory import npartitions


def test_partitions():
    """
    Calculate the number of partitions of a non-negative integer k.
    
    This function returns the number of partitions of a non-negative integer k.
    The number of partitions of k is the number of ways k can be expressed as
    a sum of positive integers, where the order of addends does not matter.
    
    Parameters:
    k (int): A non-negative integer whose number of partitions is to be calculated.
    
    Returns:
    int: The number of partitions of k.
    
    Examples:
    >>> test_partitions()
    True
    """

    assert [npartitions(k) for k in range(13)] == \
        [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77]
    assert npartitions(100) == 190569292
    assert npartitions(200) == 3972999029388
    assert npartitions(1000) == 24061467864032622473692149727991
    assert npartitions(2000) == 4720819175619413888601432406799959512200344166
    assert npartitions(10000) % 10**10 == 6916435144
    assert npartitions(100000) % 10**10 == 9421098519
