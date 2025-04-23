from sympy.combinatorics.group_constructs import DirectProduct
from sympy.combinatorics.named_groups import CyclicGroup, DihedralGroup


def test_direct_product_n():
    """
    Generate a direct product of cyclic and dihedral groups.
    
    This function creates direct products of cyclic and dihedral groups and checks their properties.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Properties of the Groups:
    - CyclicGroup(4): A cyclic group of order 4.
    - DihedralGroup(4): A dihedral group of order 8.
    - DirectProduct(C, C, C): A direct product of three cyclic groups of order
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
