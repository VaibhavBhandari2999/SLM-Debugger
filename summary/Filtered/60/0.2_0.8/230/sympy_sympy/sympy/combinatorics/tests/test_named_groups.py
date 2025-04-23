from sympy.combinatorics.named_groups import (SymmetricGroup, CyclicGroup,
DihedralGroup, AlternatingGroup, AbelianGroup)


def test_SymmetricGroup():
    """
    Tests the SymmetricGroup class.
    
    This function tests the SymmetricGroup class by creating instances of it with different sizes and checking various properties and methods.
    
    Key Parameters:
    - None
    
    Keywords:
    - None
    
    Returns:
    - None
    
    Assertions:
    - The size of the first generator of a SymmetricGroup of size 5 is 5.
    - The number of elements in the generated SymmetricGroup of size 5 is 120.
    - The SymmetricGroup of size 5 is not
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
    Tests the DihedralGroup function.
    
    This function checks the properties of the DihedralGroup function for different orders. It generates the group and verifies its order, transitivity, abelian property, solvability, and nilpotency.
    
    Parameters:
    - No explicit parameters are needed for this function.
    
    Returns:
    - None: This function does not return any value. It prints the results of the tests.
    
    Key Properties Tested:
    - Order of the group.
    - Transitivity.
    - Abelian property
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
    """
    Generate the alternating group of a given degree.
    
    This function creates the alternating group of a specified degree. The alternating group is the group of even permutations of a finite set.
    
    Parameters:
    n (int): The degree (number of elements) of the set for which the alternating group is generated.
    
    Returns:
    PermutationGroup: The alternating group of the specified degree.
    
    Key Points:
    - The function returns a PermutationGroup object.
    - For n=1 or n=2, the group order
    """

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
