from sympy.physics.quantum import Dagger
from sympy.physics.quantum.boson import BosonOp
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.operatorordering import (normal_order,
                                                 normal_ordered_form)


def test_normal_order():
    """
    Normalize the order of bosonic and fermionic operators.
    
    This function normalizes the order of operators in a given expression.
    For bosonic operators (BosonOp), it ensures that the creation operator
    (Dagger) appears before the annihilation operator (a). For fermionic
    operators (FermionOp), it ensures that the creation operator (Dagger)
    appears after the annihilation operator (c).
    
    Parameters:
    a (BosonOp): A bosonic annihilation operator
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
    Test the normal_ordered_form function for Boson and Fermion operators.
    
    This function tests the normal_ordered_form function for both Boson and Fermion operators. It checks the normal ordering of various combinations of creation and annihilation operators.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function tests the normal ordering of Boson and Fermion operators.
    - It checks the normal ordering for single and multiple operators.
    - The function uses BosonOp and FermionOp
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
