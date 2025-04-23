from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing import cxxcode

x = Symbol('x')

def test_using():
    """
    Using directive for C++ standard library vector.
    
    Parameters:
    v (str): The C++ type to be used in the using directive.
    alias (str, optional): An alias for the type. If not provided, the alias will be 'std::vector'.
    
    Returns:
    str: The generated using directive as a string.
    
    Examples:
    >>> test_using()
    'using std::vector'
    >>> test_using('vec')
    'using vec = std
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
