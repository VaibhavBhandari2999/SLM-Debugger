import matplotlib.gridspec as gridspec
import pytest


def test_equal():
    """
    Test for equality in a GridSpec object.
    
    This function checks for equality of GridSpec objects. It asserts that a GridSpec object is equal to itself and that a slice of the GridSpec object is equal to itself.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    gs (GridSpec): A GridSpec object from matplotlib.
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
    of it. The representation includes the slicing or ratio specifications
    used to define the GridSpec.
    
    Parameters:
    ss (GridSpec): The GridSpec object to be represented as a string.
    
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
