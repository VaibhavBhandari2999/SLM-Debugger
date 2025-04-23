from sympy.physics.quantum import Dagger, AntiCommutator, qapply
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.fermion import FermionFockKet, FermionFockBra


def test_fermionoperator():
    """
    Test the FermionOp class.
    
    This function checks the functionality of the FermionOp class, which is used to represent fermionic operators. It verifies the creation of fermionic and anti-fermionic operators, their properties, and the anti-commutation relations between them.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Creates FermionOp instances for annihilation and anti-fermionic operators.
    - Verifies the properties of the created operators.
    - Checks the anti-commutation relations
    """

    c = FermionOp('c')
    d = FermionOp('d')

    assert isinstance(c, FermionOp)
    assert isinstance(Dagger(c), FermionOp)

    assert c.is_annihilation
    assert not Dagger(c).is_annihilation

    assert FermionOp("c") == FermionOp("c", True)
    assert FermionOp("c") != FermionOp("d")
    assert FermionOp("c", True) != FermionOp("c", False)

    assert AntiCommutator(c, Dagger(c)).doit() == 1

    assert AntiCommutator(c, Dagger(d)).doit() == c * Dagger(d) + Dagger(d) * c


def test_fermion_states():
    c = FermionOp("c")

    # Fock states
    assert (FermionFockBra(0) * FermionFockKet(1)).doit() == 0
    assert (FermionFockBra(1) * FermionFockKet(1)).doit() == 1

    assert qapply(c * FermionFockKet(1)) == FermionFockKet(0)
    assert qapply(c * FermionFockKet(0)) == 0

    assert qapply(Dagger(c) * FermionFockKet(0)) == FermionFockKet(1)
    assert qapply(Dagger(c) * FermionFockKet(1)) == 0
