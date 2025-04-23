from sympy.core.compatibility import ordered
from sympy.combinatorics.partitions import (Partition, IntegerPartition,
                                            RGS_enum, RGS_unrank, RGS_rank,
                                            random_integer_partition)
from sympy.testing.pytest import raises
from sympy.utilities.iterables import default_sort_key, partitions
from sympy.sets.sets import Set, FiniteSet


def test_partition_constructor():
    """
    Construct a Partition object.
    
    This function validates the input to ensure that the two sets provided are
    disjoint and cover the entire set of elements. It raises a ValueError if the
    input does not meet these criteria.
    
    Parameters:
    a (iterable or FiniteSet): The first set of elements.
    b (iterable or FiniteSet): The second set of elements.
    
    Returns:
    Partition: A Partition object representing the disjoint sets a and b.
    
    Raises:
    ValueError: If the input sets
    """

    raises(ValueError, lambda: Partition([1, 1, 2]))
    raises(ValueError, lambda: Partition([1, 2, 3], [2, 3, 4]))
    raises(ValueError, lambda: Partition(1, 2, 3))
    raises(ValueError, lambda: Partition(*list(range(3))))

    assert Partition([1, 2, 3], [4, 5]) == Partition([4, 5], [1, 2, 3])
    assert Partition({1, 2, 3}, {4, 5}) == Partition([1, 2, 3], [4, 5])

    a = FiniteSet(1, 2, 3)
    b = FiniteSet(4, 5)
    assert Partition(a, b) == Partition([1, 2, 3], [4, 5])
    assert Partition({a, b}) == Partition(FiniteSet(a, b))
    assert Partition({a, b}) != Partition(a, b)

def test_partition():
    from sympy.abc import x

    a = Partition([1, 2, 3], [4])
    b = Partition([1, 2], [3, 4])
    c = Partition([x])
    l = [a, b, c]
    l.sort(key=default_sort_key)
    assert l == [c, a, b]
    l.sort(key=lambda w: default_sort_key(w, order='rev-lex'))
    assert l == [c, a, b]

    assert (a == b) is False
    assert a <= b
    assert (a > b) is False
    assert a != b
    assert a < b

    assert (a + 2).partition == [[1, 2], [3, 4]]
    assert (b - 1).partition == [[1, 2, 4], [3]]

    assert (a - 1).partition == [[1, 2, 3, 4]]
    assert (a + 1).partition == [[1, 2, 4], [3]]
    assert (b + 1).partition == [[1, 2], [3], [4]]

    assert a.rank == 1
    assert b.rank == 3

    assert a.RGS == (0, 0, 0, 1)
    assert b.RGS == (0, 0, 1, 1)


def test_integer_partition():
    # no zeros in partition
    raises(ValueError, lambda: IntegerPartition(list(range(3))))
    # check fails since 1 + 2 != 100
    raises(ValueError, lambda: IntegerPartition(100, list(range(1, 3))))
    a = IntegerPartition(8, [1, 3, 4])
    b = a.next_lex()
    c = IntegerPartition([1, 3, 4])
    d = IntegerPartition(8, {1: 3, 3: 1, 2: 1})
    assert a == c
    assert a.integer == d.integer
    assert a.conjugate == [3, 2, 2, 1]
    assert (a == b) is False
    assert a <= b
    assert (a > b) is False
    assert a != b

    for i in range(1, 11):
        next = set()
        prev = set()
        a = IntegerPartition([i])
        ans = {IntegerPartition(p) for p in partitions(i)}
        n = len(ans)
        for j in range(n):
            next.add(a)
            a = a.next_lex()
            IntegerPartition(i, a.partition)  # check it by giving i
        for j in range(n):
            prev.add(a)
            a = a.prev_lex()
            IntegerPartition(i, a.partition)  # check it by giving i
        assert next == ans
        assert prev == ans

    assert IntegerPartition([1, 2, 3]).as_ferrers() == '###\n##\n#'
    assert IntegerPartition([1, 1, 3]).as_ferrers('o') == 'ooo\no\no'
    assert str(IntegerPartition([1, 1, 3])) == '[3, 1, 1]'
    assert IntegerPartition([1, 1, 3]).partition == [3, 1, 1]

    raises(ValueError, lambda: random_integer_partition(-1))
    assert random_integer_partition(1) == [1]
    assert random_integer_partition(10, seed=[1, 3, 2, 1, 5, 1]
            ) == [5, 2, 1, 1, 1]


def test_rgs():
    """
    Generate a restricted growth string (RGS) from a given rank and size.
    
    Parameters:
    rank (int): The rank of the RGS to generate.
    size (int): The size of the RGS.
    
    Returns:
    list: The generated RGS.
    
    Raises:
    ValueError: If the rank is negative or if the size is less than 1.
    ValueError: If the rank is out of the valid range for the given size.
    
    Example:
    >>> RGS_unrank(
    """

    raises(ValueError, lambda: RGS_unrank(-1, 3))
    raises(ValueError, lambda: RGS_unrank(3, 0))
    raises(ValueError, lambda: RGS_unrank(10, 1))

    raises(ValueError, lambda: Partition.from_rgs(list(range(3)), list(range(2))))
    raises(ValueError, lambda: Partition.from_rgs(list(range(1, 3)), list(range(2))))
    assert RGS_enum(-1) == 0
    assert RGS_enum(1) == 1
    assert RGS_unrank(7, 5) == [0, 0, 1, 0, 2]
    assert RGS_unrank(23, 14) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 2]
    assert RGS_rank(RGS_unrank(40, 100)) == 40

def test_ordered_partition_9608():
    """
    Test ordered partitioning of two partitions.
    
    This function checks if the ordered partitioning of two given partitions, `a` and `b`, is correct. The partitions are instances of the `Partition` class and are compared using the `_infimum_key` method of the `Set` class to determine their order.
    
    Parameters:
    a (Partition): The first partition.
    b (Partition): The second partition.
    
    Returns:
    None: The function asserts the correctness of the ordered partitioning. If
    """

    a = Partition([1, 2, 3], [4])
    b = Partition([1, 2], [3, 4])
    assert list(ordered([a,b], Set._infimum_key))
