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
    Compare two lists of permutations to check if they are equal.
    
    This function verifies if two lists of permutations are the same, regardless of the order of elements within the lists. It is used to test the equality of permutation lists generated in different ways.
    
    Parameters:
    els (list): The first list of permutations to compare.
    other (list): The second list of permutations to compare.
    
    Returns:
    bool: True if the two lists contain the same permutations, False otherwise.
    
    Example:
    >>> S
    """

    S = SymmetricGroup(4)
    els = list(S.generate_dimino())
    other = els[:]
    shuffle(other)
    assert _cmp_perm_lists(els, other) is True


def test_naive_list_centralizer():
    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    assert _naive_list_centralizer(S, S) == [Permutation([0, 1, 2])]
    assert PermutationGroup(_naive_list_centralizer(S, A)).is_subgroup(A)


def test_verify_bsgs():
    """
    Verify the correctness of the Schreier-Sims algorithm for a given symmetric group.
    
    This function checks if the Schreier-Sims algorithm has been correctly applied to a symmetric group.
    It ensures that the base and strong generating set (SGS) are consistent with the group's structure.
    
    Parameters:
    S (SymmetricGroup): The symmetric group object for which the Schreier-Sims algorithm was applied.
    base (list): The base of the symmetric group, a list of points used
    """

    S = SymmetricGroup(5)
    S.schreier_sims()
    base = S.base
    strong_gens = S.strong_gens
    assert _verify_bsgs(S, base, strong_gens) is True
    assert _verify_bsgs(S, base[:-1], strong_gens) is False
    assert _verify_bsgs(S, base, S.generators) is False


def test_verify_centralizer():
    """
    Verify that the centralizer of one group within another is correct.
    
    This function checks whether the provided centralizer group is indeed the centralizer of the first group within the second group.
    
    Parameters:
    group1 (PermutationGroup): The first group.
    group2 (PermutationGroup): The second group, which is supposed to contain the first group.
    centr (PermutationGroup): The candidate centralizer of group1 within group2.
    
    Returns:
    bool: True if the candidate centralizer
    """

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

