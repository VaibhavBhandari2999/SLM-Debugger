from sympy import sqrt, exp, prod, Rational
from sympy.physics.quantum import Dagger, Commutator, qapply
from sympy.physics.quantum.boson import BosonOp
from sympy.physics.quantum.boson import (
    BosonFockKet, BosonFockBra, BosonCoherentKet, BosonCoherentBra)


def test_bosonoperator():
    """
    Test BosonOperator.
    
    This function tests the BosonOperator class, which is used to represent bosonic operators in quantum mechanics. It verifies the creation of BosonOp instances, checks the properties of annihilation and creation operators, and tests the commutator function for different operators.
    
    Parameters:
    None
    
    Returns:
    None
    """

    a = BosonOp('a')
    b = BosonOp('b')

    assert isinstance(a, BosonOp)
    assert isinstance(Dagger(a), BosonOp)

    assert a.is_annihilation
    assert not Dagger(a).is_annihilation

    assert BosonOp("a") == BosonOp("a", True)
    assert BosonOp("a") != BosonOp("c")
    assert BosonOp("a", True) != BosonOp("a", False)

    assert Commutator(a, Dagger(a)).doit() == 1

    assert Commutator(a, Dagger(b)).doit() == a * Dagger(b) - Dagger(b) * a


def test_boson_states():
    """
    Test Boson states.
    
    This function tests the properties of Boson states, including Fock states and coherent states. It verifies the orthogonality and normalization of Fock states, and the overlap and expectation values of coherent states. It also checks the action of the boson annihilation operator on coherent states.
    
    Key Parameters:
    - a: Boson operator.
    
    Input:
    - No explicit input parameters. The function uses predefined boson operators and states.
    
    Output:
    - The function does not return any
    """

    a = BosonOp("a")

    # Fock states
    n = 3
    assert (BosonFockBra(0) * BosonFockKet(1)).doit() == 0
    assert (BosonFockBra(1) * BosonFockKet(1)).doit() == 1
    assert qapply(BosonFockBra(n) * Dagger(a)**n * BosonFockKet(0)) \
        == sqrt(prod(range(1, n+1)))

    # Coherent states
    alpha1, alpha2 = 1.2, 4.3
    assert (BosonCoherentBra(alpha1) * BosonCoherentKet(alpha1)).doit() == 1
    assert (BosonCoherentBra(alpha2) * BosonCoherentKet(alpha2)).doit() == 1
    assert abs((BosonCoherentBra(alpha1) * BosonCoherentKet(alpha2)).doit() -
               exp((alpha1 - alpha2) ** 2 * Rational(-1, 2))) < 1e-12
    assert qapply(a * BosonCoherentKet(alpha1)) == \
        alpha1 * BosonCoherentKet(alpha1)
