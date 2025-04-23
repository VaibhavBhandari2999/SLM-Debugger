import matplotlib.gridspec as gridspec
import pytest


def test_equal():
    """
    Test equality of grid spec entries.
    
    This function checks if two grid spec entries are equal.
    
    Parameters:
    gs (GridSpec): The GridSpec object to be tested.
    
    Returns:
    None: This function does not return any value. It only checks for equality and asserts the result.
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
    ss = gridspec.GridSpec(3, 3)[2, 1:3]
    assert repr(ss) == "GridSpec(3, 3)[2:3, 1:3]"

    ss = gridspec.GridSpec(2, 2,
                           height_ratios=(3, 1),
                           width_ratios=(1, 3))
    assert repr(ss) == \
        "GridSpec(2, 2, height_ratios=(3, 1), width_ratios=(1, 3))"
