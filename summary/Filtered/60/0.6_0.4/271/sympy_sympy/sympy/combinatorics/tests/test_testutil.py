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
    Generate the centralizer of a group H in a group G.
    
    This function returns a list of permutations that form the centralizer of a given subgroup H in a group G. The centralizer of H in G is the set of all elements in G that commute with every element in H.
    
    Parameters:
    G (PermutationGroup): The group in which to find the centralizer.
    H (PermutationGroup): The subgroup whose centralizer is to be found.
    
    Returns:
    list: A
    """

    # verified by GAP
    S = SymmetricGroup(3)
    A = AlternatingGroup(3)
    assert _naive_list_centralizer(S, S) == [Permutation([0, 1, 2])]
    assert PermutationGroup(_naive_list_centralizer(S, A)).is_subgroup(A)


def test_verify_bsgs():
    """
    Verify the correctness of the Schreier-Sims algorithm for a given symmetric group.
    
    This function checks if the Schreier-Sims algorithm has been correctly applied to a symmetric group by verifying the base and strong generating set.
    
    Parameters:
    S (SymmetricGroup): The symmetric group object for which the Schreier-Sims algorithm was applied.
    base (list): The base of the symmetric group, a list of points.
    strong_gens (list): The strong generating set of the
    """

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
