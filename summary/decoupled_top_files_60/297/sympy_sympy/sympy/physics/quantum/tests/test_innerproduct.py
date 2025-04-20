from sympy.core.numbers import (I, Integer)

from sympy.physics.quantum.innerproduct import InnerProduct
from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.state import Bra, Ket, StateBase


def test_innerproduct():
    """
    Test the inner product functionality.
    
    This function checks the creation and manipulation of inner products between
    a bra and a ket. It ensures that the inner product is correctly instantiated,
    and that operations involving inner products are handled as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations:
    - Instantiation of an inner product from a bra and a ket.
    - Multiplication of kets and bras to form inner products.
    - Substitution of a bra with its dagger in an
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
    f = FooKet('foo')
    b = BarBra('bar')
    assert InnerProduct(b, f).doit() == I
    assert InnerProduct(Dagger(f), Dagger(b)).doit() == -I
    assert InnerProduct(Dagger(f), f).doit() == Integer(1)
