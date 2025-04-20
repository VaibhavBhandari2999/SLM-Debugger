import bisect
from collections import defaultdict

from sympy.combinatorics import Permutation
from sympy.core.containers import Tuple
from sympy.core.numbers import Integer


def _get_mapping_from_subranks(subranks):
    """
    Generate a mapping from subranks to their corresponding (rank, subrank) pairs.
    
    This function takes a list of subranks and returns a dictionary that maps each integer to a tuple (rank, subrank).
    The integer is a unique identifier for each subrank, and the tuple indicates the rank and subrank it belongs to.
    
    Parameters:
    subranks (list of int): A list of integers representing the number of subranks for each rank.
    
    Returns:
    dict: A
    """

    mapping = {}
    counter = 0
    for i, rank in enumerate(subranks):
        for j in range(rank):
            mapping[counter] = (i, j)
            counter += 1
    return mapping


def _get_contraction_links(args, subranks, *contraction_indices):
    """
    Generates contraction links for tensor operations.
    
    This function takes a set of arguments, subranks, and contraction indices to generate a dictionary of contraction links. Each link is represented as a tuple of tuples, where each inner tuple contains an argument and a position.
    
    Parameters:
    args (list): A list of arguments representing the tensors.
    subranks (list): A list of subranks corresponding to each argument.
    *contraction_indices (tuple): Variable length argument list of tuples,
    """

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
    Get the index of an element in a list of subindices.
    
    This function searches for an element `ind` within a list of subindices `subindices`. The subindices can be individual elements or sets of elements. If `ind` is found as a standalone element or as a member of a set, the function returns its index. If `ind` is not found, an IndexError is raised.
    
    Parameters:
    subindices (list): A list of subindices, which can be individual elements
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
    
    This function takes a function `func` and a nested list or tuple `arr`. It applies `func` to each element in `arr`, including elements of nested lists or tuples, and returns a new nested structure with the results.
    
    Parameters:
    func (callable): The function to apply to each element.
    arr (list, tuple): The nested list or tuple to process.
    
    Returns:
    list or tuple: A new nested list or
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
        if j in flattened_contraction_indices:
            return None
        else:
            return j - func(j)

    return transform


def _build_push_indices_down_func_transformation(flattened_contraction_indices):
    """
    Build a transformation function for shifting indices in a tensor contraction.
    
    This function generates a transformation function that can be used to shift the indices of a tensor contraction. The transformation is necessary when the contraction involves a reduction operation that collapses certain dimensions.
    
    Parameters:
    flattened_contraction_indices (list): A list of integers representing the indices that are being contracted.
    
    Returns:
    function: A transformation function that takes an index and returns the corresponding shifted index.
    
    Example:
    >>> transform = _build_push_indices_down_func
    """

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
