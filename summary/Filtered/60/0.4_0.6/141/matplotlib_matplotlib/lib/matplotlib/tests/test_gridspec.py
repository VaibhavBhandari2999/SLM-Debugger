import matplotlib.gridspec as gridspec
import pytest


def test_equal():
    """
    Test for equality in GridSpec.
    
    This function checks the equality of GridSpec objects in a 2x1 GridSpec.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the equality check fails for the specified GridSpec indices.
    
    Usage:
    test_equal()
    """

    gs = gridspec.GridSpec(2, 1)
    assert gs[0, 0] == gs[0, 0]
    assert gs[:, 0] == gs[:, 0]


def test_width_ratios():
    """
    Addresses issue #5835.
    See at https://github.com/matplotlib/matplotlib/issues/5835.
    """
    with pytest.raises(ValueError):
        gridspec.GridSpec(1, 1, width_ratios=[2, 1, 3])


def test_height_ratios():
    """
    Addresses issue #5835.
    See at https://github.com/matplotlib/matplotlib/issues/5835.
    """
    with pytest.raises(ValueError):
        gridspec.GridSpec(1, 1, height_ratios=[2, 1, 3])


def test_repr():
    """
    Generate a string representation of a GridSpec object.
    
    This function takes a GridSpec object and returns a string representation
    of the object. The representation includes the slicing or ratio information
    used to define the GridSpec.
    
    Parameters:
    ss (GridSpec): A GridSpec object defined using slicing or ratios.
    
    Returns:
    str: A string representation of the GridSpec object.
    """

    ss = gridspec.GridSpec(3, 3)[2, 1:3]
    assert repr(ss) == "GridSpec(3, 3)[2:3, 1:3]"

    ss = gridspec.GridSpec(2, 2,
                           height_ratios=(3, 1),
                           width_ratios=(1, 3))
    assert repr(ss) == \
        "GridSpec(2, 2, height_ratios=(3, 1), width_ratios=(1, 3))"
