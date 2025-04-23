from sympy import binomial_coefficients, binomial_coefficients_list, multinomial_coefficients
from sympy.ntheory.multinomial import multinomial_coefficients_iterator


def test_binomial_coefficients_list():
    assert binomial_coefficients_list(0) == [1]
    assert binomial_coefficients_list(1) == [1, 1]
    assert binomial_coefficients_list(2) == [1, 2, 1]
    assert binomial_coefficients_list(3) == [1, 3, 3, 1]
    assert binomial_coefficients_list(4) == [1, 4, 6, 4, 1]
    assert binomial_coefficients_list(5) == [1, 5, 10, 10, 5, 1]
    assert binomial_coefficients_list(6) == [1, 6, 15, 20, 15, 6, 1]


def test_binomial_coefficients():
    """
    Tests the correctness of the binomial_coefficients function.
    
    This function iterates over a range of values from 0 to n (inclusive) and checks if the generated binomial coefficients match the expected values.
    
    Parameters:
    - n (int): The maximum value for which to generate binomial coefficients.
    
    Returns:
    - None: This function does not return any value. It only asserts the correctness of the binomial_coefficients function.
    
    Note:
    - The binomial_coefficients function should return a dictionary where the
    """

    for n in range(15):
        c = binomial_coefficients(n)
        l = [c[k] for k in sorted(c)]
        assert l == binomial_coefficients_list(n)


def test_multinomial_coefficients():
    """
    Generate multinomial coefficients for a given partition.
    
    This function calculates the multinomial coefficients for a given partition of
    a positive integer `n` into `k` parts, where `k` is the number of parts.
    
    Parameters:
    n (int): The total number to partition.
    k (int): The number of parts to partition `n` into.
    
    Returns:
    dict: A dictionary where keys are tuples representing the partition and
    values are the corresponding multinomial coefficients.
    
    Example:
    """

    assert multinomial_coefficients(1, 1) == {(1,): 1}
    assert multinomial_coefficients(1, 2) == {(2,): 1}
    assert multinomial_coefficients(1, 3) == {(3,): 1}
    assert multinomial_coefficients(2, 0) == {(0, 0): 1}
    assert multinomial_coefficients(2, 1) == {(0, 1): 1, (1, 0): 1}
    assert multinomial_coefficients(2, 2) == {(2, 0): 1, (0, 2): 1, (1, 1): 2}
    assert multinomial_coefficients(2, 3) == {(3, 0): 1, (1, 2): 3, (0, 3): 1,
            (2, 1): 3}
    assert multinomial_coefficients(3, 1) == {(1, 0, 0): 1, (0, 1, 0): 1,
            (0, 0, 1): 1}
    assert multinomial_coefficients(3, 2) == {(0, 1, 1): 2, (0, 0, 2): 1,
            (1, 1, 0): 2, (0, 2, 0): 1, (1, 0, 1): 2, (2, 0, 0): 1}
    mc = multinomial_coefficients(3, 3)
    assert mc == {(2, 1, 0): 3, (0, 3, 0): 1,
            (1, 0, 2): 3, (0, 2, 1): 3, (0, 1, 2): 3, (3, 0, 0): 1,
            (2, 0, 1): 3, (1, 2, 0): 3, (1, 1, 1): 6, (0, 0, 3): 1}
    assert dict(multinomial_coefficients_iterator(2, 0)) == {(0, 0): 1}
    assert dict(
        multinomial_coefficients_iterator(2, 1)) == {(0, 1): 1, (1, 0): 1}
    assert dict(multinomial_coefficients_iterator(2, 2)) == \
        {(2, 0): 1, (0, 2): 1, (1, 1): 2}
    assert dict(multinomial_coefficients_iterator(3, 3)) == mc
    it = multinomial_coefficients_iterator(7, 2)
    assert [next(it) for i in range(4)] == \
        [((2, 0, 0, 0, 0, 0, 0), 1), ((1, 1, 0, 0, 0, 0, 0), 2),
      ((0, 2, 0, 0, 0, 0, 0), 1), ((1, 0, 1, 0, 0, 0, 0), 2)]
