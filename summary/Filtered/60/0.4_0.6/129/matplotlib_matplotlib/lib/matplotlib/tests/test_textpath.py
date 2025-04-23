import copy

from matplotlib.textpath import TextPath


def test_copy():
    """
    Test the deep copy and shallow copy of a TextPath object.
    
    Parameters:
    None
    
    Returns:
    None
    
    This function checks the behavior of deep copy and shallow copy operations on a TextPath object. It verifies that a deep copy results in a new set of vertices that are not the same object as the original, while a shallow copy shares the same vertices as the original.
    """

    tp = TextPath((0, 0), ".")
    assert copy.deepcopy(tp).vertices is not tp.vertices
    assert (copy.deepcopy(tp).vertices == tp.vertices).all()
    assert copy.copy(tp).vertices is tp.vertices
