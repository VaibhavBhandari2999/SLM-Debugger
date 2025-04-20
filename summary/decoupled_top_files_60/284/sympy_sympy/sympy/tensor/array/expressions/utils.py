import bisect
from collections import defaultdict

from sympy import Tuple, Integer


def _get_mapping_from_subranks(subranks):
    mapping = {}
    counter = 0
    for i, rank in enumerate(subranks):
        for j in range(rank):
            mapping[counter] = (i, j)
            counter += 1
    return mapping


def _get_contraction_links(args, subranks, *contraction_indices):
    """
    Generate contraction links for tensor operations.
    
    This function computes the contraction links for a given set of tensor arguments and subranks. It returns a dictionary of links and the original arguments.
    
    Parameters:
    args (list): A list of tensor arguments.
    subranks (list): A list of subranks corresponding to each tensor argument.
    *contraction_indices (tuple): Variable length argument list of tuples, where each tuple contains pairs of tensor arguments and their respective positions for contraction.
    
    Returns:
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
    """
    Get the diagonal indices from a list of tensor indices.
    
    This function processes a list of tensor indices to identify and separate the diagonal indices from the rest. The diagonal indices are those that involve contractions over the same axis multiple times.
    
    Parameters:
    flattened_indices (list): A list of tensor indices, which can be integers or symbolic indices.
    
    Returns:
    tuple: A tuple containing two elements:
    - diagonal_indices (list of tuples): A list of tuples, where each tuple contains the indices that
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
    for i, sind in enumerate(subindices):
        if ind == sind:
            return i
        if isinstance(sind, (set, frozenset)) and ind in sind:
            return i
    raise IndexError("%s not found in %s" % (ind, subindices))


def _apply_recursively_over_nested_lists(func, arr):
    if isinstance(arr, (tuple, list, Tuple)):
        return tuple(_apply_recursively_over_nested_lists(func, i) for i in arr)
    elif isinstance(arr, Tuple):
        return Tuple.fromiter(_apply_recursively_over_nested_lists(func, i) for i in arr)
    else:
        return func(arr)


def _build_push_indices_up_func_transformation(flattened_contraction_indices):
    """
    Builds a function to transform indices by shifting them up based on a given set of flattened contraction indices.
    
    Parameters:
    flattened_contraction_indices (list): A list of integers representing the flattened contraction indices.
    
    Returns:
    function: A function that takes an index as input and returns the transformed index.
    
    The function creates a transformation that shifts indices up based on the provided flattened contraction indices. It uses a dictionary to store cumulative shifts and a helper function to perform the transformation.
    """

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
        Transforms an index `j` based on predefined shifts.
        
        This function takes an index `j` and applies a transformation based on the `shifts` list. If `j` is within the range of the `shifts` list, it returns the corresponding value from `shifts`. Otherwise, it calculates a new index by adding the last element of `shifts` to `j` and adjusting for the length of `shifts`.
        
        Parameters:
        j (int): The original index
        """

        if j in flattened_contraction_indices:
            return None
        else:
            return j - func(j)

    return transform


def _build_push_indices_down_func_transformation(flattened_contraction_indices):
    """
    Builds a function to transform indices for pushing down contractions in a tensor network.
    
    This function generates a transformation function that maps original indices to new indices
    after pushing down contractions in a tensor network. The transformation is based on a list
    of flattened contraction indices.
    
    Parameters:
    flattened_contraction_indices (list): A list of integers representing the indices
    where contractions are to be pushed down.
    
    Returns:
    function: A function that takes an index `j` and returns the transformed
    """

    N = flattened_contraction_indices[-1]+2

    shifts = [i for i in range(N) if i not in flattened_contraction_indices]

    def transform(j):
        if j < len(shifts):
            return shifts[j]
        else:
            return j + shifts[-1] - len(shifts) + 1

    return transform
