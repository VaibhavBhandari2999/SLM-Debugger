from sympy.physics.quantum import Dagger, AntiCommutator, qapply
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.fermion import FermionFockKet, FermionFockBra


def test_fermionoperator():
    c = FermionOp('c')
    d = FermionOp('d')

    assert isinstance(c, FermionOp)
    assert isinstance(Dagger(c), FermionOp)

    assert c.is_annihilation
    assert not Dagger(c).is_annihilation

    assert FermionOp("c") == FermionOp("c")
    assert FermionOp("c") != FermionOp("d")
    assert FermionOp("c", True) != FermionOp("c", False)

    assert AntiCommutator(c, Dagger(c)).doit() == 1

    assert AntiCommutator(c, Dagger(d)).doit() == c * Dagger(d) + Dagger(d) * c


def test_fermion_states():
    """
    Test the behavior of fermionic states and operators.
    
    This function tests the interaction between fermionic creation and annihilation operators (c and Dagger(c)) and fermionic Fock states (FermionFockBra and FermionFockKet).
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function asserts the correct behavior of the fermionic annihilation and creation operators on Fock states.
    - It checks that the annihilation operator (c) acting on a Fock state
    """

    c = FermionOp("c")

    # Fock states
    assert (FermionFockBra(0) * FermionFockKet(1)).doit() == 0
    assert (FermionFockBra(1) * FermionFockKet(1)).doit() == 1

    assert qapply(c * FermionFockKet(1)) == FermionFockKet(0)
    assert qapply(c * FermionFockKet(0)) == 0

    assert qapply(Dagger(c) * FermionFockKet(0)) == FermionFockKet(1)
    assert qapply(Dagger(c) * FermionFockKet(1)) == 0
et(1)) == 0
