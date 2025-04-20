from sympy.core.numbers import Rational
from sympy.ntheory.egyptian_fraction import egyptian_fraction
from sympy.core.add import Add
from sympy.testing.pytest import raises
from sympy.core.random import random_complex_number


def test_egyptian_fraction():
    """
    Test the Egyptian fraction representation of a rational number.
    
    This function tests the correctness of the Egyptian fraction representation
    for a given rational number. It supports different algorithms for generating
    the fractions.
    
    Parameters:
    - r (Rational): The rational number to be tested.
    - alg (str, optional): The algorithm to use for generating the Egyptian
    fraction. Supported algorithms are 'Greedy', 'Takenouchi', 'Graham Jewett',
    and 'Golomb'. Default is 'Gre
    """

    def test_equality(r, alg="Greedy"):
        return r == Add(*[Rational(1, i) for i in egyptian_fraction(r, alg)])

    r = random_complex_number(a=0, c=1, b=0, d=0, rational=True)
    assert test_equality(r)

    assert egyptian_fraction(Rational(4, 17)) == [5, 29, 1233, 3039345]
    assert egyptian_fraction(Rational(7, 13), "Greedy") == [2, 26]
    assert egyptian_fraction(Rational(23, 101), "Greedy") == \
        [5, 37, 1438, 2985448, 40108045937720]
    assert egyptian_fraction(Rational(18, 23), "Takenouchi") == \
        [2, 6, 12, 35, 276, 2415]
    assert egyptian_fraction(Rational(5, 6), "Graham Jewett") == \
        [6, 7, 8, 9, 10, 42, 43, 44, 45, 56, 57, 58, 72, 73, 90, 1806, 1807,
         1808, 1892, 1893, 1980, 3192, 3193, 3306, 5256, 3263442, 3263443,
         3267056, 3581556, 10192056, 10650056950806]
    assert egyptian_fraction(Rational(5, 6), "Golomb") == [2, 6, 12, 20, 30]
    assert egyptian_fraction(Rational(5, 121), "Golomb") == [25, 1225, 3577, 7081, 11737]
    raises(ValueError, lambda: egyptian_fraction(Rational(-4, 9)))
    assert egyptian_fraction(Rational(8, 3), "Golomb") == [1, 2, 3, 4, 5, 6, 7,
                                                           14, 574, 2788, 6460,
                                                           11590, 33062, 113820]
    assert egyptian_fraction(Rational(355, 113)) == [1, 2, 3, 4, 5, 6, 7, 8, 9,
                                                     10, 11, 12, 27, 744, 893588,
                                                     1251493536607,
                                                     20361068938197002344405230]


def test_input():
    """
    Generate Egyptian fractions for a given rational number or tuple of integers using a specified method.
    
    Parameters:
    - value (Union[Rational, Tuple[int, int], Tuple[int, int, int]]): The input value for which to generate Egyptian fractions. Can be a Rational number or a tuple representing a fraction (numerator, denominator) or a tuple of integers.
    - method (str): The method to use for generating Egyptian fractions. Supported methods include 'Greedy', 'Graham Jewett
    """

    r = (2,3), Rational(2, 3), (Rational(2), Rational(3))
    for m in ["Greedy", "Graham Jewett", "Takenouchi", "Golomb"]:
        for i in r:
            d = egyptian_fraction(i, m)
            assert all(i.is_Integer for i in d)
            if m == "Graham Jewett":
                assert d == [3, 4, 12]
            else:
                assert d == [2, 6]
    # check prefix
    d = egyptian_fraction(Rational(5, 3))
    assert d == [1, 2, 6] and all(i.is_Integer for i in d)
