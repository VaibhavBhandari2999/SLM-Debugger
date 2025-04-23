from sympy import (sqrt, sin, cos, diff, conjugate,
                   mathieus, mathieuc, mathieusprime, mathieucprime)

from sympy.abc import a, q, z


def test_mathieus():
    """
    Test the Mathieu function.
    
    This function evaluates the Mathieu function for given parameters a, q, and z.
    
    Parameters:
    a (sympy.Symbol): The characteristic value of the Mathieu function.
    q (sympy.Symbol): The parameter of the Mathieu function.
    z (sympy.Symbol): The argument of the Mathieu function.
    
    Returns:
    sympy.Function: The Mathieu function evaluated at the given parameters and argument.
    
    Key Properties:
    - The function
    """

    assert isinstance(mathieus(a, q, z), mathieus)
    assert mathieus(a, 0, z) == sin(sqrt(a)*z)
    assert conjugate(mathieus(a, q, z)) == mathieus(conjugate(a), conjugate(q), conjugate(z))
    assert diff(mathieus(a, q, z), z) == mathieusprime(a, q, z)

def test_mathieuc():
    assert isinstance(mathieuc(a, q, z), mathieuc)
    assert mathieuc(a, 0, z) == cos(sqrt(a)*z)
    assert diff(mathieuc(a, q, z), z) == mathieucprime(a, q, z)

def test_mathieusprime():
    """
    Generate the Mathieu prime function.
    
    This function computes the Mathieu prime function, which is a special function
    related to the Mathieu differential equation. The function is defined for
    given parameters a, q, and z.
    
    Parameters:
    a (float): The characteristic value of the Mathieu function.
    q (float): The parameter of the Mathieu function.
    z (float): The argument of the Mathieu prime function.
    
    Returns:
    mathieusprime (function): The Math
    """

    assert isinstance(mathieusprime(a, q, z), mathieusprime)
    assert mathieusprime(a, 0, z) == sqrt(a)*cos(sqrt(a)*z)
    assert diff(mathieusprime(a, q, z), z) == (-a + 2*q*cos(2*z))*mathieus(a, q, z)

def test_mathieucprime():
    assert isinstance(mathieucprime(a, q, z), mathieucprime)
    assert mathieucprime(a, 0, z) == -sqrt(a)*sin(sqrt(a)*z)
    assert diff(mathieucprime(a, q, z), z) == (-a + 2*q*cos(2*z))*mathieuc(a, q, z)
*mathieuc(a, q, z)
