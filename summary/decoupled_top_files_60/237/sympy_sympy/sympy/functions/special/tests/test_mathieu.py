from sympy import (sqrt, sin, cos, diff, conjugate,
                   mathieus, mathieuc, mathieusprime, mathieucprime)

from sympy.abc import a, q, z


def test_mathieus():
    assert isinstance(mathieus(a, q, z), mathieus)
    assert mathieus(a, 0, z) == sin(sqrt(a)*z)
    assert conjugate(mathieus(a, q, z)) == mathieus(conjugate(a), conjugate(q), conjugate(z))
    assert diff(mathieus(a, q, z), z) == mathieusprime(a, q, z)

def test_mathieuc():
    """
    Generate a Mathieu function of parameter a and characteristic q.
    
    This function returns a Mathieu function of the specified parameter a and characteristic q evaluated at z.
    
    Parameters:
    a (float): The parameter of the Mathieu function.
    q (float): The characteristic or tuning parameter of the Mathieu function.
    z (float): The point at which the Mathieu function is evaluated.
    
    Returns:
    mathieuc: A Mathieu function object representing the Mathieu function evaluated at z.
    
    Raises
    """

    assert isinstance(mathieuc(a, q, z), mathieuc)
    assert mathieuc(a, 0, z) == cos(sqrt(a)*z)
    assert diff(mathieuc(a, q, z), z) == mathieucprime(a, q, z)

def test_mathieusprime():
    assert isinstance(mathieusprime(a, q, z), mathieusprime)
    assert mathieusprime(a, 0, z) == sqrt(a)*cos(sqrt(a)*z)
    assert diff(mathieusprime(a, q, z), z) == (-a + 2*q*cos(2*z))*mathieus(a, q, z)

def test_mathieucprime():
    assert isinstance(mathieucprime(a, q, z), mathieucprime)
    assert mathieucprime(a, 0, z) == -sqrt(a)*sin(sqrt(a)*z)
    assert diff(mathieucprime(a, q, z), z) == (-a + 2*q*cos(2*z))*mathieuc(a, q, z)
