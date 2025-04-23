from sympy.core.numbers import (I, Integer)

from sympy.physics.quantum.innerproduct import InnerProduct
from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.state import Bra, Ket, StateBase


def test_innerproduct():
    """
    Test the inner product functionality.
    
    This function checks the creation and manipulation of inner products using Ket and Bra objects. It verifies the creation of an InnerProduct object, the assignment of bra and ket, and the behavior of multiplication and substitution.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Operations:
    - Creation of an InnerProduct object.
    - Assignment of bra and ket.
    - Multiplication operations involving InnerProduct.
    - Substitution of bra with its dagger.
    """

    k = Ket('k')
    b = Bra('b')
    ip = InnerProduct(b, k)
    assert isinstance(ip, InnerProduct)
    assert ip.bra == b
    assert ip.ket == k
    assert b*k == InnerProduct(b, k)
    assert k*(b*k)*b == k*InnerProduct(b, k)*b
    assert InnerProduct(b, k).subs(b, Dagger(k)) == Dagger(k)*k


def test_innerproduct_dagger():
    k = Ket('k')
    b = Bra('b')
    ip = b*k
    assert Dagger(ip) == Dagger(k)*Dagger(b)


class FooState(StateBase):
    pass


class FooKet(Ket, FooState):

    @classmethod
    def dual_class(self):
        return FooBra

    def _eval_innerproduct_FooBra(self, bra):
        return Integer(1)

    def _eval_innerproduct_BarBra(self, bra):
        return I


class FooBra(Bra, FooState):
    @classmethod
    def dual_class(self):
        return FooKet


class BarState(StateBase):
    pass


class BarKet(Ket, BarState):
    @classmethod
    def dual_class(self):
        return BarBra


class BarBra(Bra, BarState):
    @classmethod
    def dual_class(self):
        return BarKet


def test_doit():
    """
    Test the inner product of quantum states.
    
    This function calculates the inner product of various quantum states and their
    daggered counterparts. It uses the `InnerProduct` function to compute the
    result of the inner product and the `doit` method to evaluate it.
    
    Parameters:
    None
    
    Returns:
    None
    """

    f = FooKet('foo')
    b = BarBra('bar')
    assert InnerProduct(b, f).doit() == I
    assert InnerProduct(Dagger(f), Dagger(b)).doit() == -I
    assert InnerProduct(Dagger(f), f).doit() == Integer(1)
