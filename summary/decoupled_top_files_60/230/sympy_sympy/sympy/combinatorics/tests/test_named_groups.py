from sympy.combinatorics.named_groups import (SymmetricGroup, CyclicGroup,
DihedralGroup, AlternatingGroup, AbelianGroup)


def test_SymmetricGroup():
    """
    Tests the SymmetricGroup class.
    
    This function tests the SymmetricGroup class by creating instances with different sizes and checking various properties and methods.
    
    Key Parameters:
    - None
    
    Keywords:
    - None
    
    Input:
    - None
    
    Output:
    - Assertions to check the correctness of the SymmetricGroup class.
    
    Methods Called:
    - SymmetricGroup(size): Creates a symmetric group of the specified size.
    - generate(): Generates all elements of the group.
    - generators[0].size: Checks the size of the first
    """

    G = SymmetricGroup(5)
    elements = list(G.generate())
    assert (G.generators[0]).size == 5
    assert len(elements) == 120
    assert G.is_solvable is False
    assert G.is_abelian is False
    assert G.is_nilpotent is False
    assert G.is_transitive() is True
    H = SymmetricGroup(1)
    assert H.order() == 1
    L = SymmetricGroup(2)
    assert L.order() == 2


def test_CyclicGroup():
    G = CyclicGroup(10)
    elements = list(G.generate())
    assert len(elements) == 10
    assert (G.derived_subgroup()).order() == 1
    assert G.is_abelian is True
    assert G.is_solvable is True
    assert G.is_nilpotent is True
    H = CyclicGroup(1)
    assert H.order() == 1
    L = CyclicGroup(2)
    assert L.order() == 2


def test_DihedralGroup():
    """
    Test the DihedralGroup function.
    
    This function tests the DihedralGroup function to ensure it returns a group of the correct order, and checks if the group is transitive, abelian, solvable, and nilpotent. It also tests the special cases for DihedralGroup(1) and DihedralGroup(2).
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The length of the generated elements list is 12.
    - The group is transitive.
    """

    G = DihedralGroup(6)
    elements = list(G.generate())
    assert len(elements) == 12
    assert G.is_transitive() is True
    assert G.is_abelian is False
    assert G.is_solvable is True
    assert G.is_nilpotent is False
    H = DihedralGroup(1)
    assert H.order() == 2
    L = DihedralGroup(2)
    assert L.order() == 4
    assert L.is_abelian is True
    assert L.is_nilpotent is True


def test_AlternatingGroup():
    G = AlternatingGroup(5)
    elements = list(G.generate())
    assert len(elements) == 60
    assert [perm.is_even for perm in elements] == [True]*60
    H = AlternatingGroup(1)
    assert H.order() == 1
    L = AlternatingGroup(2)
    assert L.order() == 1


def test_AbelianGroup():
    A = AbelianGroup(3, 3, 3)
    assert A.order() == 27
    assert A.is_abelian is True
