from sympy import Sieve, sieve
from sympy.core.compatibility import range

from sympy.ntheory import isprime, totient, randprime, nextprime, prevprime, \
    primerange, primepi, prime, primorial, composite, compositepi, reduced_totient
from sympy.ntheory.generate import cycle_length
from sympy.ntheory.primetest import mr
from sympy.utilities.pytest import raises


def test_prime():
    """
    Generate the nth prime number.
    
    This function calculates the nth prime number using a sieve algorithm. It supports large values of n and includes error handling for invalid inputs.
    
    Parameters:
    n (int): The position of the prime number to return.
    
    Returns:
    int: The nth prime number.
    
    Raises:
    ValueError: If the input is less than 1.
    
    Additional Notes:
    - The function uses a sieve algorithm for efficient prime number generation.
    - The sieve is extended up to 30
    """

    assert prime(1) == 2
    assert prime(2) == 3
    assert prime(5) == 11
    assert prime(11) == 31
    assert prime(57) == 269
    assert prime(296) == 1949
    assert prime(559) == 4051
    assert prime(3000) == 27449
    assert prime(4096) == 38873
    assert prime(9096) == 94321
    assert prime(25023) == 287341
    raises(ValueError, lambda: prime(0))
    sieve.extend(3000)
    assert prime(401) == 2749


def test_primepi():
    """
    Calculate the prime counting function, π(n), which returns the number of prime numbers less than or equal to n.
    
    Parameters:
    n (int): The upper limit integer to count primes up to.
    
    Returns:
    int: The number of prime numbers less than or equal to n.
    
    Examples:
    >>> test_primepi()
    True
    >>> primepi(1)
    0
    >>> primepi(2)
    1
    >>> primepi(5)
    3
    """

    assert primepi(1) == 0
    assert primepi(2) == 1
    assert primepi(5) == 3
    assert primepi(11) == 5
    assert primepi(57) == 16
    assert primepi(296) == 62
    assert primepi(559) == 102
    assert primepi(3000) == 430
    assert primepi(4096) == 564
    assert primepi(9096) == 1128
    assert primepi(25023) == 2763
    assert primepi(10**8) == 5761455
    assert primepi(253425253) == 13856396
    assert primepi(8769575643) == 401464322
    sieve.extend(3000)
    assert primepi(2000) == 303


def test_composite():
    from sympy.ntheory.generate import sieve
    sieve._reset()
    assert composite(1) == 4
    assert composite(2) == 6
    assert composite(5) == 10
    assert composite(11) == 20
    assert composite(41) == 58
    assert composite(57) == 80
    assert composite(296) == 370
    assert composite(559) == 684
    assert composite(3000) == 3488
    assert composite(4096) == 4736
    assert composite(9096) == 10368
    assert composite(25023) == 28088
    sieve.extend(3000)
    assert composite(1957) == 2300
    assert composite(2568) == 2998
    raises(ValueError, lambda: composite(0))


def test_compositepi():
    assert compositepi(1) == 0
    assert compositepi(2) == 0
    assert compositepi(5) == 1
    assert compositepi(11) == 5
    assert compositepi(57) == 40
    assert compositepi(296) == 233
    assert compositepi(559) == 456
    assert compositepi(3000) == 2569
    assert compositepi(4096) == 3531
    assert compositepi(9096) == 7967
    assert compositepi(25023) == 22259
    assert compositepi(10**8) == 94238544
    assert compositepi(253425253) == 239568856
    assert compositepi(8769575643) == 8368111320
    sieve.extend(3000)
    assert compositepi(2321) == 1976


def test_generate():
    """
    Generate a sequence of prime numbers and related functions.
    
    Key functions include:
    - nextprime: Returns the smallest prime number greater than the given value.
    - prevprime: Returns the largest prime number smaller than the given value.
    - primerange: Returns a list of prime numbers within a specified range.
    - Sieve: A class for generating and working with prime numbers.
    - cycle_length: Computes the cycle length of a function.
    - mr: Performs the Miller-Rabin primality test.
    
    Parameters:
    -
    """

    from sympy.ntheory.generate import sieve
    sieve._reset()
    assert nextprime(-4) == 2
    assert nextprime(2) == 3
    assert nextprime(5) == 7
    assert nextprime(12) == 13
    assert prevprime(3) == 2
    assert prevprime(7) == 5
    assert prevprime(13) == 11
    assert prevprime(19) == 17
    assert prevprime(20) == 19

    sieve.extend_to_no(9)
    assert sieve._list[-1] == 23

    assert sieve._list[-1] < 31
    assert 31 in sieve

    assert nextprime(90) == 97
    assert nextprime(10**40) == (10**40 + 121)
    assert prevprime(97) == 89
    assert prevprime(10**40) == (10**40 - 17)
    assert list(sieve.primerange(10, 1)) == []
    assert list(primerange(10, 1)) == []
    assert list(primerange(2, 7)) == [2, 3, 5]
    assert list(primerange(2, 10)) == [2, 3, 5, 7]
    assert list(primerange(1050, 1100)) == [1051, 1061,
        1063, 1069, 1087, 1091, 1093, 1097]
    s = Sieve()
    for i in range(30, 2350, 376):
        for j in range(2, 5096, 1139):
            A = list(s.primerange(i, i + j))
            B = list(primerange(i, i + j))
            assert A == B
    s = Sieve()
    assert s[10] == 29

    assert nextprime(2, 2) == 5

    raises(ValueError, lambda: totient(0))

    raises(ValueError, lambda: reduced_totient(0))

    raises(ValueError, lambda: primorial(0))

    assert mr(1, [2]) is False

    func = lambda i: (i**2 + 1) % 51
    assert next(cycle_length(func, 4)) == (6, 2)
    assert list(cycle_length(func, 4, values=True)) == \
        [17, 35, 2, 5, 26, 14, 44, 50, 2, 5, 26, 14]
    assert next(cycle_length(func, 4, nmax=5)) == (5, None)
    assert list(cycle_length(func, 4, nmax=5, values=True)) == \
        [17, 35, 2, 5, 26]
    sieve.extend(3000)
    assert nextprime(2968) == 2969
    assert prevprime(2930) == 2927
    raises(ValueError, lambda: prevprime(1))


def test_randprime():
    """
    Generate a random prime number within a specified range.
    
    This function generates a random prime number between two given integers, a and b (inclusive of a and exclusive of b).
    
    Parameters:
    a (int): The lower bound of the range (inclusive).
    b (int): The upper bound of the range (exclusive).
    
    Returns:
    int: A random prime number within the specified range.
    
    Raises:
    ValueError: If the lower bound is greater than or equal to the upper bound.
    
    Examples:
    >>> test_randprime
    """

    import random
    random.seed(1234)
    assert randprime(10, 1) is None
    assert randprime(2, 3) == 2
    assert randprime(1, 3) == 2
    assert randprime(3, 5) == 3
    raises(ValueError, lambda: randprime(20, 22))
    for a in [100, 300, 500, 250000]:
        for b in [100, 300, 500, 250000]:
            p = randprime(a, a + b)
            assert a <= p < (a + b) and isprime(p)


def test_primorial():
    """
    Calculate the product of the first n prime numbers.
    
    Args:
    n (int): The number of prime numbers to multiply.
    nth (int, optional): The index of the prime number to start from. Defaults to 1.
    
    Returns:
    int: The product of the first n prime numbers starting from the nth prime.
    
    Examples:
    >>> test_primorial()
    True
    >>> primorial(1)
    2
    >>> primorial(1, nth=
    """

    assert primorial(1) == 2
    assert primorial(1, nth=0) == 1
    assert primorial(2) == 6
    assert primorial(2, nth=0) == 2
    assert primorial(4, nth=0) == 6


def test_search():
    assert 2 in sieve
    assert 2.1 not in sieve
    assert 1 not in sieve
    assert 2**1000 not in sieve
    raises(ValueError, lambda: sieve.search(1))


def test_sieve_slice():
    """
    Test the slicing functionality of the sieve.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    None
    
    Notes:
    This function tests the slicing functionality of the sieve object. It checks if the 5th element of the sieve is 11 and if slicing from the 5th to the 10th element (inclusive) and with a step of 2 returns the expected values.
    """

    assert sieve[5] == 11
    assert list(sieve[5:10]) == [sieve[x] for x in range(5, 10)]
    assert list(sieve[5:10:2]) == [sieve[x] for x in range(5, 10, 2)]
