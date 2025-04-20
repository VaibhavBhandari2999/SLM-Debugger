# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os
from unittest.mock import patch

import pytest
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from astropy.io import fits

from ..core import WCSAxes
from .... import units as u
from ....tests.image_tests import ignore_matplotlibrc

ROOT = os.path.join(os.path.dirname(__file__))
MSX_HEADER = fits.Header.fromtextfile(os.path.join(ROOT, 'data', 'msx_header'))


@ignore_matplotlibrc
def test_getaxislabel():
    """
    Get the axis label for a given coordinate axis.
    
    This function retrieves the axis label set for a specific coordinate axis in a WCSAxes.
    
    Parameters:
    ax (WCSAxes): The WCSAxes object containing the coordinate system.
    
    Returns:
    str: The axis label for the specified coordinate axis.
    
    Example usage:
    >>> fig = plt.figure()
    >>> ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], aspect='
    """


    fig = plt.figure()
    ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], aspect='equal')

    ax.coords[0].set_axislabel("X")
    ax.coords[1].set_axislabel("Y")
    assert ax.coords[0].get_axislabel() == "X"
    assert ax.coords[1].get_axislabel() == "Y"


@pytest.fixture
def ax():
    fig = plt.figure()
    ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], aspect='equal')
    fig.add_axes(ax)

    return ax


def assert_label_draw(ax, x_label, y_label):
    ax.coords[0].set_axislabel("Label 1")
    ax.coords[1].set_axislabel("Label 2")

    with patch.object(ax.coords[0].axislabels, 'set_position') as pos1:
        with patch.object(ax.coords[1].axislabels, 'set_position') as pos2:
            ax.figure.canvas.draw()

    assert pos1.call_count == x_label
    assert pos2.call_count == y_label


@ignore_matplotlibrc
def test_label_visibility_rules_default(ax):
    assert_label_draw(ax, True, True)


@ignore_matplotlibrc
def test_label_visibility_rules_label(ax):
    """
    Test function to check the visibility rules for labels on a matplotlib axis.
    
    This function sets specific visibility and tick properties for the coordinate labels on a given matplotlib axis and then checks the visibility of the labels according to the specified rules.
    
    Parameters:
    ax (matplotlib.axis.Axis): The matplotlib axis object containing the coordinate labels to be tested.
    
    Returns:
    None: This function does not return any value. It asserts the visibility of the labels based on the given conditions.
    
    Key Properties:
    - The function sets
    """


    ax.coords[0].set_ticklabel_visible(False)
    ax.coords[1].set_ticks(values=[-9999]*u.one)

    assert_label_draw(ax, False, False)


@ignore_matplotlibrc
def test_label_visibility_rules_ticks(ax):
    """
    Test the visibility rules for axis labels and ticks.
    
    This function sets the axis label visibility rule to 'ticks' for both axes and
    hides the tick labels for the first axis while setting the ticks to a constant
    value that is not visible. It then checks the visibility of the labels and
    ticks using the `assert_label_draw` function.
    
    Parameters:
    ax (matplotlib.axes.Axes): The axes object containing the coordinate
    systems to be tested.
    
    Returns:
    None: This function
    """


    ax.coords[0].set_axislabel_visibility_rule('ticks')
    ax.coords[1].set_axislabel_visibility_rule('ticks')

    ax.coords[0].set_ticklabel_visible(False)
    ax.coords[1].set_ticks(values=[-9999]*u.one)

    assert_label_draw(ax, True, False)


@ignore_matplotlibrc
def test_label_visibility_rules_always(ax):

    ax.coords[0].set_axislabel_visibility_rule('always')
    ax.coords[1].set_axislabel_visibility_rule('always')

    ax.coords[0].set_ticklabel_visible(False)
    ax.coords[1].set_ticks(values=[-9999]*u.one)

    assert_label_draw(ax, True, True)


def test_set_separator(tmpdir):
    """
    Test the set_separator method for coordinate formatting in a WCSAxes.
    
    This function creates a figure and a WCSAxes object using a provided WCS header. It then forces a draw to enable the format_coord functionality. The function tests the set_separator method for changing the coordinate separator and ensures that the format_coord output is correctly updated. The method supports different types of separators and can revert to the default format.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object used for creating temporary files or directories
    """


    fig = plt.figure()
    ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], wcs=WCS(MSX_HEADER))
    fig.add_axes(ax)

    # Force a draw which is required for format_coord to work
    ax.figure.canvas.draw()

    ax.coords[1].set_format_unit('deg')
    assert ax.coords[1].format_coord(4) == '4\xb000\'00\"'
    ax.coords[1].set_separator((':', ':', ''))
    assert ax.coords[1].format_coord(4) == '4:00:00'
    ax.coords[1].set_separator('abc')
    assert ax.coords[1].format_coord(4) == '4a00b00c'
    ax.coords[1].set_separator(None)
    assert ax.coords[1].format_coord(4) == '4\xb000\'00\"'
