from sympy.combinatorics.group_constructs import DirectProduct
from sympy.combinatorics.named_groups import CyclicGroup, DihedralGroup


def test_direct_product_n():
    """
    Generate a direct product of groups.
    
    This function creates a direct product of specified groups and performs several checks on the resulting group.
    
    Parameters:
    C (CyclicGroup): A cyclic group.
    D (DihedralGroup): A dihedral group.
    
    Returns:
    DirectProduct: The direct product of the input groups.
    
    Assertions:
    - The order of the direct product of three cyclic groups of order 4 is 64.
    - The degree of the direct product of three cyclic
    """

    C = CyclicGroup(4)
    D = DihedralGroup(4)
    G = DirectProduct(C, C, C)
    assert G.order() == 64
    assert G.degree == 12
    assert len(G.orbits()) == 3
    assert G.is_abelian is True
    H = DirectProduct(D, C)
    assert H.order() == 32
    assert H.is_abelian is False
