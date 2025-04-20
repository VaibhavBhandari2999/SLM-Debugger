from sympy import symbols, Integer

from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.commutator import Commutator as Comm
from sympy.physics.quantum.operator import Operator


a, b, c = symbols('a,b,c')
A, B, C, D = symbols('A,B,C,D', commutative=False)


def test_commutator():
    """
    Test the commutator of two symbols A and B.
    
    This function computes the commutator of two symbols A and B, which is defined as [A, B] = AB - BA. The commutator is an object of type Comm and is not commutative by default. The function also checks if the commutator is correctly substituted with another symbol C for A.
    
    Parameters:
    A (Symbol): The first symbol.
    B (Symbol): The second symbol.
    
    Returns:
    """

    c = Comm(A, B)
    assert c.is_commutative is False
    assert isinstance(c, Comm)
    assert c.subs(A, C) == Comm(C, B)


def test_commutator_identities():
    assert Comm(a*A, b*B) == a*b*Comm(A, B)
    assert Comm(A, A) == 0
    assert Comm(a, b) == 0
    assert Comm(A, B) == -Comm(B, A)
    assert Comm(A, B).doit() == A*B - B*A
    assert Comm(A, B*C).expand(commutator=True) == Comm(A, B)*C + B*Comm(A, C)
    assert Comm(A*B, C*D).expand(commutator=True) == \
        A*C*Comm(B, D) + A*Comm(B, C)*D + C*Comm(A, D)*B + Comm(A, C)*D*B
    assert Comm(A + B, C + D).expand(commutator=True) == \
        Comm(A, C) + Comm(A, D) + Comm(B, C) + Comm(B, D)
    assert Comm(A, B + C).expand(commutator=True) == Comm(A, B) + Comm(A, C)
    e = Comm(A, Comm(B, C)) + Comm(B, Comm(C, A)) + Comm(C, Comm(A, B))
    assert e.doit().expand() == 0


def test_commutator_dagger():
    """
    Test the commutator of the dagger operation.
    
    This function checks the expansion of the dagger of a commutator.
    
    Parameters:
    None
    
    Returns:
    None
    """

    comm = Comm(A*B, C)
    assert Dagger(comm).expand(commutator=True) == \
        - Comm(Dagger(B), Dagger(C))*Dagger(A) - \
        Dagger(B)*Comm(Dagger(A), Dagger(C))


class Foo(Operator):

    def _eval_commutator_Bar(self, bar):
        return Integer(0)


class Bar(Operator):
    pass


class Tam(Operator):

    def _eval_commutator_Foo(self, foo):
        return Integer(1)


def test_eval_commutator():
    F = Foo('F')
    B = Bar('B')
    T = Tam('T')
    assert Comm(F, B).doit() == 0
    assert Comm(B, F).doit() == 0
    assert Comm(F, T).doit() == -1
    assert Comm(T, F).doit() == 1
    assert Comm(B, T).doit() == B*T - T*B
