import numpy as np
import matplotlib.pyplot as plt
from matplotlib import markers
from matplotlib._api.deprecation import MatplotlibDeprecationWarning
from matplotlib.path import Path
from matplotlib.testing.decorators import check_figures_equal
from matplotlib.transforms import Affine2D

import pytest


def test_marker_fillstyle():
    """
    Test the marker fill style.
    
    This function checks the behavior of the `MarkerStyle` object from the
    `matplotlib.markers` module, specifically focusing on the `fillstyle`
    attribute. It creates a `MarkerStyle` instance with a circle marker and
    no fill, then verifies that the fill style is correctly set to 'none' and
    that the marker is not filled.
    
    Args:
    None
    
    Returns:
    None
    
    Attributes:
    marker_style
    """

    marker_style = markers.MarkerStyle(marker='o', fillstyle='none')
    assert marker_style.get_fillstyle() == 'none'
    assert not marker_style.is_filled()


@pytest.mark.parametrize('marker', [
    'o',
    'x',
    '',
    'None',
    r'$\frac{1}{2}$',
    "$\u266B$",
    1,
    markers.TICKLEFT,
    [[-1, 0], [1, 0]],
    np.array([[-1, 0], [1, 0]]),
    Path([[0, 0], [1, 0]], [Path.MOVETO, Path.LINETO]),
    (5, 0),  # a pentagon
    (7, 1),  # a 7-pointed star
    (5, 2),  # asterisk
    (5, 0, 10),  # a pentagon, rotated by 10 degrees
    (7, 1, 10),  # a 7-pointed star, rotated by 10 degrees
    (5, 2, 10),  # asterisk, rotated by 10 degrees
    markers.MarkerStyle('o'),
])
def test_markers_valid(marker):
    # Checking this doesn't fail.
    markers.MarkerStyle(marker)


def test_deprecated_marker():
    """
    Test the deprecated marker functionality.
    
    This function checks the behavior of the `MarkerStyle` class when using
    deprecated markers. It verifies that warnings are raised when creating an
    instance with a deprecated marker, but not when creating a copy of such an
    instance.
    
    Parameters:
    None
    
    Returns:
    None
    """

    with pytest.warns(MatplotlibDeprecationWarning):
        ms = markers.MarkerStyle()
    markers.MarkerStyle(ms)  # No warning on copy.
    with pytest.warns(MatplotlibDeprecationWarning):
        ms = markers.MarkerStyle(None)
    markers.MarkerStyle(ms)  # No warning on copy.


@pytest.mark.parametrize('marker', [
    'square',  # arbitrary string
    np.array([[-0.5, 0, 1, 2, 3]]),  # 1D array
    (1,),
    (5, 3),  # second parameter of tuple must be 0, 1, or 2
    (1, 2, 3, 4),
])
def test_markers_invalid(marker):
    with pytest.raises(ValueError):
        markers.MarkerStyle(marker)


class UnsnappedMarkerStyle(markers.MarkerStyle):
    """
    A MarkerStyle where the snap threshold is force-disabled.

    This is used to compare to polygon/star/asterisk markers which do not have
    any snap threshold set.
    """
    def _recache(self):
        super()._recache()
        self._snap_threshold = None


@check_figures_equal()
def test_poly_marker(fig_test, fig_ref):
    """
    Test the equivalence of polygon markers in two figures.
    
    Parameters:
    -----------
    fig_test : matplotlib.figure.Figure
    The figure containing the test scatter plots.
    fig_ref : matplotlib.figure.Figure
    The reference figure containing the expected scatter plots.
    
    Returns:
    --------
    None
    This function does not return anything. It visually compares the
    scatter plots in `fig_test` and `fig_ref` to ensure that polygon
    markers are rendered equivalently.
    """

    ax_test = fig_test.add_subplot()
    ax_ref = fig_ref.add_subplot()

    # Note, some reference sizes must be different because they have unit
    # *length*, while polygon markers are inscribed in a circle of unit
    # *radius*. This introduces a factor of np.sqrt(2), but since size is
    # squared, that becomes 2.
    size = 20**2

    # Squares
    ax_test.scatter([0], [0], marker=(4, 0, 45), s=size)
    ax_ref.scatter([0], [0], marker='s', s=size/2)

    # Diamonds, with and without rotation argument
    ax_test.scatter([1], [1], marker=(4, 0), s=size)
    ax_ref.scatter([1], [1], marker=UnsnappedMarkerStyle('D'), s=size/2)
    ax_test.scatter([1], [1.5], marker=(4, 0, 0), s=size)
    ax_ref.scatter([1], [1.5], marker=UnsnappedMarkerStyle('D'), s=size/2)

    # Pentagon, with and without rotation argument
    ax_test.scatter([2], [2], marker=(5, 0), s=size)
    ax_ref.scatter([2], [2], marker=UnsnappedMarkerStyle('p'), s=size)
    ax_test.scatter([2], [2.5], marker=(5, 0, 0), s=size)
    ax_ref.scatter([2], [2.5], marker=UnsnappedMarkerStyle('p'), s=size)

    # Hexagon, with and without rotation argument
    ax_test.scatter([3], [3], marker=(6, 0), s=size)
    ax_ref.scatter([3], [3], marker='h', s=size)
    ax_test.scatter([3], [3.5], marker=(6, 0, 0), s=size)
    ax_ref.scatter([3], [3.5], marker='h', s=size)

    # Rotated hexagon
    ax_test.scatter([4], [4], marker=(6, 0, 30), s=size)
    ax_ref.scatter([4], [4], marker='H', s=size)

    # Octagons
    ax_test.scatter([5], [5], marker=(8, 0, 22.5), s=size)
    ax_ref.scatter([5], [5], marker=UnsnappedMarkerStyle('8'), s=size)

    ax_test.set(xlim=(-0.5, 5.5), ylim=(-0.5, 5.5))
    ax_ref.set(xlim=(-0.5, 5.5), ylim=(-0.5, 5.5))


def test_star_marker():
    """
    Create a scatter plot with custom star markers.
    
    This function generates a scatter plot using Matplotlib with two points marked by custom star markers. The first point uses a default star marker, while the second point uses a star marker with a specified orientation. Both markers are scaled to the same size.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The created figure object containing the scatter plot.
    ax (matplotlib.axes.Axes): The axes object containing the scatter plot
    """

    # We don't really have a strict equivalent to this marker, so we'll just do
    # a smoke test.
    size = 20**2

    fig, ax = plt.subplots()
    ax.scatter([0], [0], marker=(5, 1), s=size)
    ax.scatter([1], [1], marker=(5, 1, 0), s=size)
    ax.set(xlim=(-0.5, 0.5), ylim=(-0.5, 1.5))


# The asterisk marker is really a star with 0-size inner circle, so the ends
# are corners and get a slight bevel. The reference markers are just singular
# lines without corners, so they have no bevel, and we need to add a slight
# tolerance.
@check_figures_equal(tol=1.45)
def test_asterisk_marker(fig_test, fig_ref, request):
    """
    Test the rendering of asterisk markers on a plot.
    
    This function compares the rendering of asterisk markers on two figures,
    `fig_test` and `fig_ref`. It adds subplots to both figures, draws asterisk
    markers with specified styles and sizes, and sets the limits of the x and y
    axes.
    
    Parameters:
    fig_test (matplotlib.figure.Figure): The figure containing the test plot.
    fig_ref (matplotlib.figure.Figure): The figure containing the
    """

    ax_test = fig_test.add_subplot()
    ax_ref = fig_ref.add_subplot()

    # Note, some reference sizes must be different because they have unit
    # *length*, while asterisk markers are inscribed in a circle of unit
    # *radius*. This introduces a factor of np.sqrt(2), but since size is
    # squared, that becomes 2.
    size = 20**2

    def draw_ref_marker(y, style, size):
        """
        Draws reference markers on a plot.
        
        This function adds reference markers at a specified y-coordinate with a given style and size. The markers are added twice due to antialiasing effects, which can slightly alter the appearance of the resulting PNG images.
        
        Parameters:
        y (float): The y-coordinate where the reference marker should be placed.
        style (str): The style of the marker to be drawn.
        size (int): The size of the marker.
        
        Returns:
        None:
        """

        # As noted above, every line is doubled. Due to antialiasing, these
        # doubled lines make a slight difference in the .png results.
        ax_ref.scatter([y], [y], marker=UnsnappedMarkerStyle(style), s=size)
        if request.getfixturevalue('ext') == 'png':
            ax_ref.scatter([y], [y], marker=UnsnappedMarkerStyle(style),
                           s=size)

    # Plus
    ax_test.scatter([0], [0], marker=(4, 2), s=size)
    draw_ref_marker(0, '+', size)
    ax_test.scatter([0.5], [0.5], marker=(4, 2, 0), s=size)
    draw_ref_marker(0.5, '+', size)

    # Cross
    ax_test.scatter([1], [1], marker=(4, 2, 45), s=size)
    draw_ref_marker(1, 'x', size/2)

    ax_test.set(xlim=(-0.5, 1.5), ylim=(-0.5, 1.5))
    ax_ref.set(xlim=(-0.5, 1.5), ylim=(-0.5, 1.5))


@check_figures_equal()
def test_marker_clipping(fig_ref, fig_test):
    """
    Test marker clipping behavior.
    
    This function compares how singular and multiple markers are clipped in
    different backend paths by plotting them on a figure with specified size
    and layout. It iterates over a set of predefined markers, placing them at
    specific coordinates and ensuring they are clipped correctly.
    
    Parameters:
    fig_ref (matplotlib.figure.Figure): The reference figure object.
    fig_test (matplotlib.figure.Figure): The test figure object.
    
    Returns:
    None: The function modifies
    """

    # Plotting multiple markers can trigger different optimized paths in
    # backends, so compare single markers vs multiple to ensure they are
    # clipped correctly.
    marker_count = len(markers.MarkerStyle.markers)
    marker_size = 50
    ncol = 7
    nrow = marker_count // ncol + 1

    width = 2 * marker_size * ncol
    height = 2 * marker_size * nrow * 2
    fig_ref.set_size_inches((width / fig_ref.dpi, height / fig_ref.dpi))
    ax_ref = fig_ref.add_axes([0, 0, 1, 1])
    fig_test.set_size_inches((width / fig_test.dpi, height / fig_ref.dpi))
    ax_test = fig_test.add_axes([0, 0, 1, 1])

    for i, marker in enumerate(markers.MarkerStyle.markers):
        x = i % ncol
        y = i // ncol * 2

        # Singular markers per call.
        ax_ref.plot([x, x], [y, y + 1], c='k', linestyle='-', lw=3)
        ax_ref.plot(x, y, c='k',
                    marker=marker, markersize=marker_size, markeredgewidth=10,
                    fillstyle='full', markerfacecolor='white')
        ax_ref.plot(x, y + 1, c='k',
                    marker=marker, markersize=marker_size, markeredgewidth=10,
                    fillstyle='full', markerfacecolor='white')

        # Multiple markers in a single call.
        ax_test.plot([x, x], [y, y + 1], c='k', linestyle='-', lw=3,
                     marker=marker, markersize=marker_size, markeredgewidth=10,
                     fillstyle='full', markerfacecolor='white')

    ax_ref.set(xlim=(-0.5, ncol), ylim=(-0.5, 2 * nrow))
    ax_test.set(xlim=(-0.5, ncol), ylim=(-0.5, 2 * nrow))
    ax_ref.axis('off')
    ax_test.axis('off')


def test_marker_init_transforms():
    """Test that initializing marker with transform is a simple addition."""
    marker = markers.MarkerStyle("o")
    t = Affine2D().translate(1, 1)
    t_marker = markers.MarkerStyle("o", transform=t)
    assert marker.get_transform() + t == t_marker.get_transform()


def test_marker_init_joinstyle():
    """
    Initialize a marker with a specified style and join style.
    
    This function creates a `MarkerStyle` object with a given marker shape and join style. It then checks if the join style is correctly set for the styled marker and ensures that the original marker's join style remains unchanged.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `markers.MarkerStyle`: Creates a marker style object.
    - `get_joinstyle`: Retrieves the current join style of a marker
    """

    marker = markers.MarkerStyle("*")
    jstl = markers.JoinStyle.round
    styled_marker = markers.MarkerStyle("*", joinstyle=jstl)
    assert styled_marker.get_joinstyle() == jstl
    assert marker.get_joinstyle() != jstl


def test_marker_init_captyle():
    """
    Initialize a marker with a specified style and cap style.
    
    This function creates a `MarkerStyle` object with a star ('*') symbol and a round cap style. It then checks if the cap style of the styled marker matches the specified cap style and ensures that the original marker's cap style is different from the specified one.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `markers.MarkerStyle`
    - `markers.CapStyle.round`
    - `
    """

    marker = markers.MarkerStyle("*")
    capstl = markers.CapStyle.round
    styled_marker = markers.MarkerStyle("*", capstyle=capstl)
    assert styled_marker.get_capstyle() == capstl
    assert marker.get_capstyle() != capstl


@pytest.mark.parametrize("marker,transform,expected", [
    (markers.MarkerStyle("o"), Affine2D().translate(1, 1),
        Affine2D().translate(1, 1)),
    (markers.MarkerStyle("o", transform=Affine2D().translate(1, 1)),
        Affine2D().translate(1, 1), Affine2D().translate(2, 2)),
    (markers.MarkerStyle("$|||$", transform=Affine2D().translate(1, 1)),
     Affine2D().translate(1, 1), Affine2D().translate(2, 2)),
    (markers.MarkerStyle(
        markers.TICKLEFT, transform=Affine2D().translate(1, 1)),
        Affine2D().translate(1, 1), Affine2D().translate(2, 2)),
])
def test_marker_transformed(marker, transform, expected):
    """
    Transforms a given marker using a specified transformation.
    
    Args:
    marker (Marker): The marker to be transformed.
    transform (Transform): The transformation to apply to the marker.
    expected (Transform): The expected user transform after applying the transformation.
    
    Returns:
    None: This function does not return any value. It asserts that the transformed marker is different from the original marker, has the expected user transform, and that the user transforms are not the same object.
    
    Important Functions:
    """

    new_marker = marker.transformed(transform)
    assert new_marker is not marker
    assert new_marker.get_user_transform() == expected
    assert marker._user_transform is not new_marker._user_transform


def test_marker_rotated_invalid():
    """
    Test that attempting to rotate an invalid marker style raises a ValueError.
    
    This function checks that calling `rotated()` on a marker style object
    without a valid marker type results in a ValueError being raised. It
    also ensures that specifying both degrees and radians for rotation
    simultaneously leads to a ValueError.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the marker is not valid or if both degrees and radians are specified for rotation.
    
    Functions
    """

    marker = markers.MarkerStyle("o")
    with pytest.raises(ValueError):
        new_marker = marker.rotated()
    with pytest.raises(ValueError):
        new_marker = marker.rotated(deg=10, rad=10)


@pytest.mark.parametrize("marker,deg,rad,expected", [
    (markers.MarkerStyle("o"), 10, None, Affine2D().rotate_deg(10)),
    (markers.MarkerStyle("o"), None, 0.01, Affine2D().rotate(0.01)),
    (markers.MarkerStyle("o", transform=Affine2D().translate(1, 1)),
        10, None, Affine2D().translate(1, 1).rotate_deg(10)),
    (markers.MarkerStyle("o", transform=Affine2D().translate(1, 1)),
        None, 0.01, Affine2D().translate(1, 1).rotate(0.01)),
    (markers.MarkerStyle("$|||$", transform=Affine2D().translate(1, 1)),
      10, None, Affine2D().translate(1, 1).rotate_deg(10)),
    (markers.MarkerStyle(
        markers.TICKLEFT, transform=Affine2D().translate(1, 1)),
        10, None, Affine2D().translate(1, 1).rotate_deg(10)),
])
def test_marker_rotated(marker, deg, rad, expected):
    """
    Rotate a marker by a specified degree or radians.
    
    Args:
    marker (Marker): The marker object to be rotated.
    deg (float): The angle of rotation in degrees.
    rad (float): The angle of rotation in radians.
    expected (Transform): The expected transformation after rotation.
    
    Returns:
    None: This function does not return anything but asserts the following conditions:
    - The rotated marker is different from the original marker.
    - The user transform of the rotated marker matches
    """

    new_marker = marker.rotated(deg=deg, rad=rad)
    assert new_marker is not marker
    assert new_marker.get_user_transform() == expected
    assert marker._user_transform is not new_marker._user_transform


def test_marker_scaled():
    """
    Create scaled marker instances.
    
    This function creates scaled marker instances using the `markers.MarkerStyle`
    class. It takes an original marker style and scales it by a given factor or
    factors. The scaling can be uniform or non-uniform along different axes.
    
    Parameters:
    None (the function uses the `markers.MarkerStyle` class directly).
    
    Returns:
    Scaled marker instances: New marker instances with applied scaling.
    
    Usage:
    - `marker.scaled(scalar)`:
    """

    marker = markers.MarkerStyle("1")
    new_marker = marker.scaled(2)
    assert new_marker is not marker
    assert new_marker.get_user_transform() == Affine2D().scale(2)
    assert marker._user_transform is not new_marker._user_transform

    new_marker = marker.scaled(2, 3)
    assert new_marker is not marker
    assert new_marker.get_user_transform() == Affine2D().scale(2, 3)
    assert marker._user_transform is not new_marker._user_transform

    marker = markers.MarkerStyle("1", transform=Affine2D().translate(1, 1))
    new_marker = marker.scaled(2)
    assert new_marker is not marker
    expected = Affine2D().translate(1, 1).scale(2)
    assert new_marker.get_user_transform() == expected
    assert marker._user_transform is not new_marker._user_transform


def test_alt_transform():
    """
    Test the equivalence of marker styles with different rotation transformations.
    
    This function compares two marker styles, `m1` and `m2`, both initialized
    with an 'o' shape and a 'left' orientation. The second marker style `m2`
    is additionally rotated by 90 degrees using an affine transformation.
    The function asserts that the alternative transform (`get_alt_transform()`)
    of both marker styles, after rotating by 90 degrees, are equivalent.
    
    Args
    """

    m1 = markers.MarkerStyle("o", "left")
    m2 = markers.MarkerStyle("o", "left", Affine2D().rotate_deg(90))
    assert m1.get_alt_transform().rotate_deg(90) == m2.get_alt_transform()
