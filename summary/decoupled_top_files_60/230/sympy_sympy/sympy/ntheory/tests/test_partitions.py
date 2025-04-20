from sympy.core.compatibility import range
from sympy.ntheory import npartitions


def test_partitions():
    """
    Calculate the number of partitions of a positive integer k.
    
    This function returns the number of partitions of a given positive integer k.
    A partition of a positive integer k is a way of writing k as a sum of positive integers.
    Two sums that differ only in the order of their summands are considered the same partition.
    
    Parameters:
    k (int): A positive integer whose partitions are to be counted.
    
    Returns:
    int: The number of partitions of the integer k.
    
    Examples:
    >>> test
    """

    assert [npartitions(k) for k in range(13)] == \
        [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77]
    assert npartitions(100) == 190569292
    assert npartitions(200) == 3972999029388
    assert npartitions(1000) == 24061467864032622473692149727991
    assert npartitions(2000) == 4720819175619413888601432406799959512200344166
    assert npartitions(10000) % 10**10 == 6916435144
    assert npartitions(100000) % 10**10 == 9421098519
