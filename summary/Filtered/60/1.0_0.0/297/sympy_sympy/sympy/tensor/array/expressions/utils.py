import bisect
from collections import defaultdict

from sympy.combinatorics import Permutation
from sympy.core.containers import Tuple
from sympy.core.numbers import Integer


def _get_mapping_from_subranks(subranks):
    mapping = {}
    counter = 0
    for i, rank in enumerate(subranks):
        for j in range(rank):
            mapping[counter] = (i, j)
            counter += 1
    return mapping


def _get_contraction_links(args, subranks, *contraction_indices):
    mapping = _get_mapping_from_subranks(subranks)
    contraction_tuples = [[mapping[j] for j in i] for i in contraction_indices]
    dlinks = defaultdict(dict)
    for links in contraction_tuples:
        if len(links) == 2:
            (arg1, pos1), (arg2, pos2) = links
            dlinks[arg1][pos1] = (arg2, pos2)
            dlinks[arg2][pos2] = (arg1, pos1)
            continue

    return args, dict(dlinks)


def _sort_contraction_indices(pairing_indices):
    pairing_indices = [Tuple(*sorted(i)) for i in pairing_indices]
    pairing_indices.sort(key=lambda x: min(x))
    return pairing_indices


def _get_diagonal_indices(flattened_indices):
    """
    Generate diagonal indices from a list of tensor indices.
    
    This function takes a list of tensor indices and identifies which indices
    should be contracted diagonally. It returns a tuple of diagonal indices and
    a modified list of indices with diagonal operations removed.
    
    Parameters:
    flattened_indices (list): A list of tensor indices, which can be integers
    or symbolic indices.
    
    Returns:
    tuple: A tuple containing:
    - diagonal_indices (list of tuples): A list of tuples, each representing
    the
    """

    axes_contraction = defaultdict(list)
    for i, ind in enumerate(flattened_indices):
        if isinstance(ind, (int, Integer)):
            # If the indices is a number, there can be no diagonal operation:
            continue
        axes_contraction[ind].append(i)
    axes_contraction = {k: v for k, v in axes_contraction.items() if len(v) > 1}
    # Put the diagonalized indices at the end:
    ret_indices = [i for i in flattened_indices if i not in axes_contraction]
    diag_indices = list(axes_contraction)
    diag_indices.sort(key=lambda x: flattened_indices.index(x))
    diagonal_indices = [tuple(axes_contraction[i]) for i in diag_indices]
    ret_indices += diag_indices
    ret_indices = tuple(ret_indices)
    return diagonal_indices, ret_indices


def _get_argindex(subindices, ind):
    """
    Get the index of an argument in a list of subindices.
    
    This function searches for a given argument `ind` within a list of subindices `subindices`. The subindices can be individual elements or sets of elements. If `ind` is found as an individual element or as a member of a set, the function returns the index of that element. If `ind` is not found, an IndexError is raised.
    
    Parameters:
    subindices (list): A list of subindices, which
    """

    for i, sind in enumerate(subindices):
        if ind == sind:
            return i
        if isinstance(sind, (set, frozenset)) and ind in sind:
            return i
    raise IndexError("%s not found in %s" % (ind, subindices))


def _apply_recursively_over_nested_lists(func, arr):
    """
    Apply a function recursively over a nested list or tuple.
    
    This function takes a function `func` and a nested list or tuple `arr`. It applies `func` to each element of `arr` and returns a new nested structure with the results. The function handles tuples and lists uniformly, ensuring that the structure of the input is preserved in the output.
    
    Parameters:
    func (callable): The function to apply to each element of the input.
    arr (list or tuple): The nested list or
    """

    if isinstance(arr, (tuple, list, Tuple)):
        return tuple(_apply_recursively_over_nested_lists(func, i) for i in arr)
    elif isinstance(arr, Tuple):
        return Tuple.fromiter(_apply_recursively_over_nested_lists(func, i) for i in arr)
    else:
        return func(arr)


def _build_push_indices_up_func_transformation(flattened_contraction_indices):
    shifts = {0: 0}
    i = 0
    cumulative = 0
    while i < len(flattened_contraction_indices):
        j = 1
        while i+j < len(flattened_contraction_indices):
            if flattened_contraction_indices[i] + j != flattened_contraction_indices[i+j]:
                break
            j += 1
        cumulative += j
        shifts[flattened_contraction_indices[i]] = cumulative
        i += j
    shift_keys = sorted(shifts.keys())

    def func(idx):
        return shifts[shift_keys[bisect.bisect_right(shift_keys, idx)-1]]

    def transform(j):
        """
        Transforms an index using a specified shift list.
        
        This function takes an index `j` and applies a transformation based on the provided `shifts` list. If the index `j` is within the range of the `shifts` list, it returns the corresponding value from `shifts`. Otherwise, it calculates a new value by adding the last element of `shifts` to `j` and adjusting for the length of `shifts`.
        
        Parameters:
        j (int): The index
        """

        if j in flattened_contraction_indices:
            return None
        else:
            return j - func(j)

    return transform


def _build_push_indices_down_func_transformation(flattened_contraction_indices):
    N = flattened_contraction_indices[-1]+2

    shifts = [i for i in range(N) if i not in flattened_contraction_indices]

    def transform(j):
        if j < len(shifts):
            return shifts[j]
        else:
            return j + shifts[-1] - len(shifts) + 1

    return transform


def _apply_permutation_to_list(perm: Permutation, target_list: list):
    """
    Permute a list according to the given permutation.
    """
    new_list = [None for i in range(perm.size)]
    for i, e in enumerate(target_list):
        new_list[perm(i)] = e
    return new_list
