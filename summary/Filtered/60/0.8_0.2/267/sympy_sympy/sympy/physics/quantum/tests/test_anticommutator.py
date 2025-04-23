from sympy import symbols, Integer

from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.anticommutator import AntiCommutator as AComm
from sympy.physics.quantum.operator import Operator


a, b, c = symbols('a,b,c')
A, B, C, D = symbols('A,B,C,D', commutative=False)


def test_anticommutator():
    """
    Test the anti-commutator of two symbols A and B.
    
    This function creates an anti-commutator object for the symbols A and B, checks its properties, and performs a substitution.
    
    Parameters:
    A (Symbol): The first symbol.
    B (Symbol): The second symbol.
    
    Returns:
    AComm: The anti-commutator object of A and B.
    
    Attributes:
    is_commutative (bool): Indicates that the anti-commutator is not commutative.
    subs (dict): Substit
    """

    ac = AComm(A, B)
    assert isinstance(ac, AComm)
    assert ac.is_commutative is False
    assert ac.subs(A, C) == AComm(C, B)


def test_commutator_identities():
    assert AComm(a*A, b*B) == a*b*AComm(A, B)
    assert AComm(A, A) == 2*A**2
    assert AComm(A, B) == AComm(B, A)
    assert AComm(a, b) == 2*a*b
    assert AComm(A, B).doit() == A*B + B*A


def test_anticommutator_dagger():
    assert Dagger(AComm(A, B)) == AComm(Dagger(A), Dagger(B))


class Foo(Operator):

    def _eval_anticommutator_Bar(self, bar):
        return Integer(0)


class Bar(Operator):
    pass


class Tam(Operator):

    def _eval_anticommutator_Foo(self, foo):
        return Integer(1)


def test_eval_commutator():
    """
    Test the commutator function for different objects.
    
    This function evaluates the commutator of various objects and checks the results.
    
    Parameters:
    F (Foo): An instance of the Foo class.
    B (Bar): An instance of the Bar class.
    T (Tam): An instance of the Tam class.
    
    Returns:
    None: This function does not return any value. It prints the results of the commutator evaluations.
    """

    F = Foo('F')
    B = Bar('B')
    T = Tam('T')
    assert AComm(F, B).doit() == 0
    assert AComm(B, F).doit() == 0
    assert AComm(F, T).doit() == 1
    assert AComm(T, F).doit() == 1
    assert AComm(B, T).doit() == B*T + T*B
