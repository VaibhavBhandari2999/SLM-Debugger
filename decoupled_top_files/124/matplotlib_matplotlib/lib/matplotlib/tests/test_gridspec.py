import matplotlib.gridspec as gridspec
import pytest


def test_equal():
    """
    Test equality of GridSpec objects.
    
    Args:
    None
    
    Returns:
    None
    
    Notes:
    - Compares two GridSpec objects at index [0, 0] using `==`.
    - Compares all GridSpec objects in the first column using `==`.
    - Utilizes the `gridspec` module for creating and comparing GridSpec objects.
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
    
    Parameters:
    -----------
    ss : GridSpec
    A GridSpec object representing a grid layout.
    
    Returns:
    --------
    str
    A string representation of the GridSpec object.
    
    Examples:
    ---------
    >>> ss = gridspec.GridSpec(3, 3)[2, 1:3]
    >>> test_repr()
    'GridSpec(3, 3)[2:3, 1:3
    """

    ss = gridspec.GridSpec(3, 3)[2, 1:3]
    assert repr(ss) == "GridSpec(3, 3)[2:3, 1:3]"

    ss = gridspec.GridSpec(2, 2,
                           height_ratios=(3, 1),
                           width_ratios=(1, 3))
    assert repr(ss) == \
        "GridSpec(2, 2, height_ratios=(3, 1), width_ratios=(1, 3))"
