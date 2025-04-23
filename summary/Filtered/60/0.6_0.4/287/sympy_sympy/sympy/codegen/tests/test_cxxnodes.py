from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing import cxxcode

x = Symbol('x')

def test_using():
    """
    Using a type alias for a C++ vector.
    
    Parameters:
    v (Type): The C++ type to alias.
    alias (str, optional): The name of the alias. Defaults to 'std::vector'.
    
    Returns:
    str: The C++ code for the using directive or type alias.
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
