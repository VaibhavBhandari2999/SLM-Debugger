from sympy.physics.quantum import Dagger
from sympy.physics.quantum.boson import BosonOp
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.operatorordering import (normal_order,
                                                 normal_ordered_form)


def test_normal_order():
    """
    Normal order the given fermionic and bosonic operators.
    
    This function takes two operators, a bosonic operator 'a' and a fermionic operator 'c', and normal orders them. Normal ordering involves moving all creation operators to the left of annihilation operators.
    
    Parameters:
    a (BosonOp): A bosonic operator.
    c (FermionOp): A fermionic operator.
    
    Returns:
    qnet.QNetExpr: The normal ordered expression.
    """

    a = BosonOp('a')

    c = FermionOp('c')

    assert normal_order(a * Dagger(a)) == Dagger(a) * a
    assert normal_order(Dagger(a) * a) == Dagger(a) * a
    assert normal_order(a * Dagger(a) ** 2) == Dagger(a) ** 2 * a

    assert normal_order(c * Dagger(c)) == - Dagger(c) * c
    assert normal_order(Dagger(c) * c) == Dagger(c) * c
    assert normal_order(c * Dagger(c) ** 2) == Dagger(c) ** 2 * c


def test_normal_ordered_form():
    """
    Test the normal_ordered_form function for Boson and Fermion operators.
    
    This function tests the normal_ordered_form function for both Boson and Fermion operators. It checks the normal ordering of various combinations of creation and annihilation operators for Bosons and Fermions.
    
    Parameters:
    a (BosonOp): Boson annihilation operator.
    c (FermionOp): Fermion annihilation operator.
    
    Returns:
    None: This function is used for testing and does not return any value.
    """

    a = BosonOp('a')

    c = FermionOp('c')

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
