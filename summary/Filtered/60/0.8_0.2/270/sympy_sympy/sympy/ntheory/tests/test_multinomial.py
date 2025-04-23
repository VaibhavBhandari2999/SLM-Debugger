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
    Generate binomial coefficients for a given integer n.
    
    This function calculates the binomial coefficients for a given integer n, which represents the number of items. The function returns a dictionary where the keys are the integers from 0 to n, and the values are the corresponding binomial coefficients.
    
    Parameters:
    n (int): The number of items to calculate binomial coefficients for.
    
    Returns:
    dict: A dictionary with keys as integers from 0 to n and values as the binomial coefficients.
    
    Example:
    >>>
    """

    for n in range(15):
        c = binomial_coefficients(n)
        l = [c[k] for k in sorted(c)]
        assert l == binomial_coefficients_list(n)


def test_multinomial_coefficients():
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
