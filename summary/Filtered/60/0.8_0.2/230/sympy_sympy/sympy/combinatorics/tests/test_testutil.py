from sympy.combinatorics.named_groups import SymmetricGroup, AlternatingGroup,\
    CyclicGroup
from sympy.combinatorics.testutil import _verify_bsgs, _cmp_perm_lists,\
    _naive_list_centralizer, _verify_centralizer,\
    _verify_normal_closure
from sympy.combinatorics.permutations import Permutation
from sympy.combinatorics.perm_groups import PermutationGroup
from random import shuffle


def test_cmp_perm_lists():
    """
    Compare two lists of permutations to check if they are identical, considering permutations as equivalent if they are the same up to a reordering.
    
    Parameters:
    els (list): The first list of permutations to compare.
    other (list): The second list of permutations to compare.
    
    Returns:
    bool: True if the two lists contain the same permutations, up to reordering; False otherwise.
    
    Note:
    This function assumes that the input lists contain SymmetricGroup elements and uses a custom comparison method `_
    """

    S = SymmetricGroup(4)
    els = list(S.generate_dimino())
    other = els[:]
    shuffle(other)
    assert _cmp_perm_lists(els, other) is True


def test_naive_list_centralizer():
    """
    Generate the centralizer of a group H in a group G.
    
    This function returns a list of permutations that form the centralizer of a subgroup H in a group G. The centralizer of H in G is the set of all elements in G that commute with every element of H.
    
    Parameters:
    G (PermutationGroup): The group in which the centralizer is to be computed.
    H (PermutationGroup): The subgroup whose centralizer in G is to be computed.
    
    Returns:
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
    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    assert _verify_normal_closure(S, A, closure=A)
    S = SymmetricGroup(5)
    A = AlternatingGroup(5)
    C = CyclicGroup(5)
    assert _verify_normal_closure(S, A, closure=A)
    assert _verify_normal_closure(S, C, closure=A)
