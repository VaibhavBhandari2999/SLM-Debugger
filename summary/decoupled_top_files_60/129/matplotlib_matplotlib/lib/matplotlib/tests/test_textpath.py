import copy

from matplotlib.textpath import TextPath


def test_copy():
    """
    Test the deep and shallow copy of a TextPath object.
    
    Parameters:
    None
    
    Returns:
    None
    
    Explanation:
    This function tests the deep and shallow copy of a TextPath object. It checks that the deep copy of the TextPath object has different vertices from the original object, but the values are the same. The shallow copy of the TextPath object shares the same vertices as the original object.
    """

    tp = TextPath((0, 0), ".")
    assert copy.deepcopy(tp).vertices is not tp.vertices
    assert (copy.deepcopy(tp).vertices == tp.vertices).all()
    assert copy.copy(tp).vertices is tp.vertices
