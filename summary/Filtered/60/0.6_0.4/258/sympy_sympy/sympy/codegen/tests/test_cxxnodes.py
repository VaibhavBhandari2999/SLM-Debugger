from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing.cxxcode import cxxcode

x = Symbol('x')

def test_using():
    """
    Using a type alias for a C++ vector.
    
    This function creates a using declaration for a C++ vector type, optionally
    renaming it.
    
    :Parameters:
    v : Type
    The C++ vector type to create a using declaration for.
    :Keyword Parameters:
    alias : str
    The name to give the vector type in the using declaration. If not
    provided, the type will be given the default 'vector' name.
    :Returns:
    A string representing the using declaration
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
