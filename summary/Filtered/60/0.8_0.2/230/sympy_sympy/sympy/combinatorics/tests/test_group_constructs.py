from sympy.combinatorics.group_constructs import DirectProduct
from sympy.combinatorics.named_groups import CyclicGroup, DihedralGroup


def test_direct_product_n():
    """
    Generate the direct product of multiple groups.
    
    This function creates the direct product of a specified number of cyclic groups.
    
    Parameters:
    n (int): The number of cyclic groups to be used in the direct product.
    
    Returns:
    DirectProduct: The resulting direct product group.
    
    Example:
    >>> test_direct_product_n()
    # The function will create and test the direct product of cyclic groups and dihedral groups.
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
