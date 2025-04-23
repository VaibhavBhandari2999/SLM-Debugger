from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing.cxxcode import cxxcode

x = Symbol('x')

def test_using():
    """
    Using the `using` function to create a type alias for a given C++ type.
    
    Parameters:
    v (Type): The C++ type to be aliased.
    alias_name (str, optional): The name of the alias. Defaults to 'std::vector'.
    
    Returns:
    str: A string representing the C++ using directive or alias.
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
