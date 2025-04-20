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
    Compare two lists of permutations to determine if they are equal.
    
    This function checks if two lists of permutations, `els` and `other`, are the same.
    The permutations in each list are compared in the same order. The function returns
    True if the lists are identical, and False otherwise.
    
    Parameters:
    els (list): A list of permutations to be compared.
    other (list): Another list of permutations to be compared against the first list.
    
    Returns:
    bool: True if the two
    """

    S = SymmetricGroup(4)
    els = list(S.generate_dimino())
    other = els[:]
    shuffle(other)
    assert _cmp_perm_lists(els, other) is True


def test_naive_list_centralizer():
    """
    Generate a list of permutations that centralize a given group within a symmetric group.
    
    This function returns a list of permutations that commute with all elements of the given group `G` within the symmetric group `S`.
    
    Parameters:
    - S (SymmetricGroup): The symmetric group in which the centralizer is to be found.
    - G (PermutationGroup): The subgroup of the symmetric group whose centralizer is to be determined.
    
    Returns:
    - list: A list of permutations that centralize the group `
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
    Verify if a group is a normal closure of a subgroup.
    
    This function checks if a given group `S` is the normal closure of a subgroup `A` within `S`.
    The normal closure of a subgroup `A` in `S` is the smallest normal subgroup of `S` that contains `A`.
    
    Parameters:
    S (Group): The group in which the normal closure is to be checked.
    A (Subgroup): The subgroup whose normal closure is to be verified.
    closure
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
