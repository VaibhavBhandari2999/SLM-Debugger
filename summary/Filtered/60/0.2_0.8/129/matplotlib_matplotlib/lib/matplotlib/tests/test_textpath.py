import copy

from matplotlib.textpath import TextPath


def test_copy():
    """
    Copies a TextPath object.
    
    This function tests the copying behavior of a TextPath object. It uses the `copy` and `deepcopy` functions to create shallow and deep copies of the TextPath object, respectively. The function checks that the deep copy has different vertices from the original, but the shallow copy shares the same vertices.
    
    Parameters:
    None
    
    Returns:
    None
    """

    tp = TextPath((0, 0), ".")
    assert copy.deepcopy(tp).vertices is not tp.vertices
    assert (copy.deepcopy(tp).vertices == tp.vertices).all()
    assert copy.copy(tp).vertices is tp.vertices
