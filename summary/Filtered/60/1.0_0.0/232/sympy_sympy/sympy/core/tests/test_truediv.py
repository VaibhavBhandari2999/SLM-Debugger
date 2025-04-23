from __future__ import division

#this module tests that sympy works with true division turned on

from sympy import Rational, Symbol, Float


def test_truediv():
    assert 1/2 != 0
    assert Rational(1)/2 != 0


def dotest(s):
    """
    dotest(s)
    Evaluate a function s on all pairs of elements from a predefined list l, which contains integers, floats, and symbolic variables. The function s is expected to take two arguments.
    
    Parameters:
    s (function): A function that takes two arguments and is to be evaluated on all pairs of elements from the list l.
    
    Returns:
    bool: True if the function s has been successfully evaluated on all pairs of elements from the list l, otherwise False.
    
    Example:
    >>> def print
    """

    x = Symbol("x")
    y = Symbol("y")
    l = [
        Rational(2),
        Float("1.3"),
        x,
        y,
        pow(x, y)*y,
        5,
        5.5
    ]
    for x in l:
        for y in l:
            s(x, y)
    return True


def test_basic():
    """
    Test the basic arithmetic operations.
    
    This function tests the basic arithmetic operations such as addition, subtraction,
    multiplication, division, and exponentiation. It does not take any parameters or
    return any value.
    
    Key operations tested:
    - Addition: a + b
    - Subtraction: a - b
    - Multiplication: a * b
    - Division: a / b
    - Exponentiation: a ** b
    
    Parameters:
    - a (int or float): The first operand.
    - b (
    """

    def s(a, b):
        x = a
        x = +a
        x = -a
        x = a + b
        x = a - b
        x = a*b
        x = a/b
        x = a**b
    assert dotest(s)


def test_ibasic():
    def s(a, b):
        x = a
        x += b
        x = a
        x -= b
        x = a
        x *= b
        x = a
        x /= b
    assert dotest(s)
= b
    assert dotest(s)
