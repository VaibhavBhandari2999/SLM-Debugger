from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing import cxxcode

x = Symbol('x')

def test_using():
    """
    Using directive for a C++ type.
    
    Parameters
    ----------
    v : Type
    The C++ type to create a using directive for.
    name : str, optional
    The name to use in the using directive. If not provided, the type name
    will be used.
    
    Returns
    -------
    str
    A string representing the using directive in C++ code.
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
