from sympy.physics.quantum import Dagger
from sympy.physics.quantum.boson import BosonOp
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.operatorordering import (normal_order,
                                                 normal_ordered_form)


def test_normal_order():
    """
    Normal order the given Boson and Fermion operators.
    
    This function takes two operators, one Boson operator and one Fermion operator, and normal orders them.
    
    Parameters:
    a (BosonOp): A Boson operator.
    b (BosonOp): Another Boson operator.
    c (FermionOp): A Fermion operator.
    d (FermionOp): Another Fermion operator.
    
    Returns:
    BosonOp or FermionOp: The normal ordered
    """

    a = BosonOp('a')
    b = BosonOp('b')

    c = FermionOp('c')
    d = FermionOp('d')

    assert normal_order(a * Dagger(a)) == Dagger(a) * a
    assert normal_order(Dagger(a) * a) == Dagger(a) * a
    assert normal_order(a * Dagger(a) ** 2) == Dagger(a) ** 2 * a

    assert normal_order(c * Dagger(c)) == - Dagger(c) * c
    assert normal_order(Dagger(c) * c) == Dagger(c) * c
    assert normal_order(c * Dagger(c) ** 2) == Dagger(c) ** 2 * c


def test_normal_ordered_form():
    """
    Tests the normal_ordered_form function for BosonOp and FermionOp objects.
    
    This function checks the normal ordering of various combinations of BosonOp and FermionOp objects. Normal ordering is the process of rearranging creation and annihilation operators in a specific order, typically with all creation operators to the left of annihilation operators.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function tests the normal ordering of BosonOp and FermionOp objects.
    - It
    """

    a = BosonOp('a')
    b = BosonOp('b')

    c = FermionOp('c')
    d = FermionOp('d')

    assert normal_ordered_form(Dagger(a) * a) == Dagger(a) * a
    assert normal_ordered_form(a * Dagger(a)) == 1 + Dagger(a) * a
    assert normal_ordered_form(a ** 2 * Dagger(a)) == \
        2 * a + Dagger(a) * a ** 2
    assert normal_ordered_form(a ** 3 * Dagger(a)) == \
        3 * a ** 2 + Dagger(a) * a ** 3

    assert normal_ordered_form(Dagger(c) * c) == Dagger(c) * c
    assert normal_ordered_form(c * Dagger(c)) == 1 - Dagger(c) * c
    assert normal_ordered_form(c ** 2 * Dagger(c)) == Dagger(c) * c ** 2
    assert normal_ordered_form(c ** 3 * Dagger(c)) == \
        c ** 2 - Dagger(c) * c ** 3
