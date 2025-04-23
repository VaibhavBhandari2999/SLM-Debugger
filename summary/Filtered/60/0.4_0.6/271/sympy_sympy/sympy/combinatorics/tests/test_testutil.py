from sympy.combinatorics.named_groups import SymmetricGroup, AlternatingGroup,\
    CyclicGroup
from sympy.combinatorics.testutil import _verify_bsgs, _cmp_perm_lists,\
    _naive_list_centralizer, _verify_centralizer,\
    _verify_normal_closure
from sympy.combinatorics.permutations import Permutation
from sympy.combinatorics.perm_groups import PermutationGroup
from random import shuffle


def test_cmp_perm_lists():
    S = SymmetricGroup(4)
    els = list(S.generate_dimino())
    other = els[:]
    shuffle(other)
    assert _cmp_perm_lists(els, other) is True


def test_naive_list_centralizer():
    """
    Generate a list of permutations that centralize a given group within a symmetric group.
    
    This function returns a list of permutations that commute with all elements of the specified group within the symmetric group of degree n.
    
    Parameters:
    group (PermutationGroup): The group for which to find the centralizer.
    symmetric_group_degree (int): The degree of the symmetric group to consider.
    
    Returns:
    list: A list of permutations that centralize the given group.
    
    Example:
    >>> S = Symmetric
    """

    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    assert _naive_list_centralizer(S, S) == [Permutation([0, 1, 2])]
    assert PermutationGroup(_naive_list_centralizer(S, A)).is_subgroup(A)


def test_verify_bsgs():
    S = SymmetricGroup(5)
    S.schreier_sims()
    base = S.base
    strong_gens = S.strong_gens
    assert _verify_bsgs(S, base, strong_gens) is True
    assert _verify_bsgs(S, base[:-1], strong_gens) is False
    assert _verify_bsgs(S, base, S.generators) is False


def test_verify_centralizer():
    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    triv = PermutationGroup([Permutation([0, 1, 2])])
    assert _verify_centralizer(S, S, centr=triv)
    assert _verify_centralizer(S, A, centr=A)


def test_verify_normal_closure():
    """
    Verify if the normal closure of a subgroup within a group is as expected.
    
    This function checks if the normal closure of a given subgroup within a specified group matches the expected closure.
    
    Parameters:
    G (Group): The group in which the normal closure is to be computed.
    H (Subgroup): The subgroup for which the normal closure is to be computed.
    closure (Group, optional): The expected normal closure of the subgroup. If not provided, it will be computed.
    
    Returns:
    bool
    """

    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    assert _verify_normal_closure(S, A, closure=A)
    S = SymmetricGroup(5)
    A = AlternatingGroup(5)
    C = CyclicGroup(5)
    assert _verify_normal_closure(S, A, closure=A)
    assert _verify_normal_closure(S, C, closure=A)
