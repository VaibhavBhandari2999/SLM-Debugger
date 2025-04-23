from sympy.physics.quantum import Dagger, AntiCommutator, qapply
from sympy.physics.quantum.fermion import FermionOp
from sympy.physics.quantum.fermion import FermionFockKet, FermionFockBra


def test_fermionoperator():
    """
    Test the FermionOp class.
    
    This function checks the functionality of the FermionOp class, including:
    - Creation of FermionOp instances.
    - Checking if an operator is an annihilation operator.
    - Comparison of FermionOp instances.
    - Anti-commutator calculation for FermionOp instances.
    
    Parameters:
    - c (FermionOp): An annihilation operator.
    - d (FermionOp): A creation operator.
    
    Returns:
    - None: This function does not return any value.
    """

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
    
    This function tests the interaction between fermionic creation (c_dag) and annihilation (c) operators and fermionic Fock states. It verifies the following:
    - The inner product between different Fock states is zero.
    - The annihilation operator acting on a Fock state reduces the occupation number by one.
    - The creation operator acting on a Fock state increases the occupation number by one.
    
    Parameters:
    - None
    
    Returns:
    - None
    """

    c = FermionOp("c")

    # Fock states
    assert (FermionFockBra(0) * FermionFockKet(1)).doit() == 0
    assert (FermionFockBra(1) * FermionFockKet(1)).doit() == 1

    assert qapply(c * FermionFockKet(1)) == FermionFockKet(0)
    assert qapply(c * FermionFockKet(0)) == 0

    assert qapply(Dagger(c) * FermionFockKet(0)) == FermionFockKet(1)
    assert qapply(Dagger(c) * FermionFockKet(1)) == 0
