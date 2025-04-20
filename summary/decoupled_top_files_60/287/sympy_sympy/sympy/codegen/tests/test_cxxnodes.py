from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing import cxxcode

x = Symbol('x')

def test_using():
    """
    Using directive for C++ standard library vector.
    
    Parameters:
    v (str): The C++ type name, in this case 'std::vector'.
    alias (str, optional): The alias to use for the using directive. Default is None, which results in 'using std::vector'.
    
    Returns:
    str: The generated C++ using directive.
    
    Examples:
    >>> test_using()
    'using std::vector'
    >>> test_using('std::vector', '
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
