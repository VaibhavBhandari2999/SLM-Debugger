from sympy.core.symbol import Symbol
from sympy.codegen.ast import Type
from sympy.codegen.cxxnodes import using
from sympy.printing.cxxcode import cxxcode

x = Symbol('x')

def test_using():
    """
    Using statement for a C++ type.
    
    Parameters
    ----------
    v : Type
    The C++ type to be used.
    name : str, optional
    The name to be used for the using statement. If not provided, the type name will be used.
    
    Returns
    -------
    str
    The generated using statement in C++ code.
    """

    v = Type('std::vector')
    u1 = using(v)
    assert cxxcode(u1) == 'using std::vector'

    u2 = using(v, 'vec')
    assert cxxcode(u2) == 'using vec = std::vector'
