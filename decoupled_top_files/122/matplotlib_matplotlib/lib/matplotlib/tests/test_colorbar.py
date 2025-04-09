import numpy as np
import pytest

from matplotlib import cm
import matplotlib.colors as mcolors

from matplotlib import rc_context
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
from matplotlib.colors import (
    BoundaryNorm, LogNorm, PowerNorm, Normalize, NoNorm
)
from matplotlib.colorbar import Colorbar
from matplotlib.ticker import FixedLocator, LogFormatter
from matplotlib.testing.decorators import check_figures_equal


def _get_cmap_norms():
    """
    Define a colormap and appropriate norms for each of the four
    possible settings of the extend keyword.

    Helper function for _colorbar_extension_shape and
    colorbar_extension_length.
    """
    # Create a colormap and specify the levels it represents.
    cmap = cm.get_cmap("RdBu", lut=5)
    clevs = [-5., -2.5, -.5, .5, 1.5, 3.5]
    # Define norms for the colormaps.
    norms = dict()
    norms['neither'] = BoundaryNorm(clevs, len(clevs) - 1)
    norms['min'] = BoundaryNorm([-10] + clevs[1:], len(clevs) - 1)
    norms['max'] = BoundaryNorm(clevs[:-1] + [10], len(clevs) - 1)
    norms['both'] = BoundaryNorm([-10] + clevs[1:-1] + [10], len(clevs) - 1)
    return cmap, norms


def _colorbar_extension_shape(spacing):
    """
    Produce 4 colorbars with rectangular extensions for either uniform
    or proportional spacing.

    Helper function for test_colorbar_extension_shape.
    """
    # Get a colormap and appropriate norms for each extension type.
    cmap, norms = _get_cmap_norms()
    # Create a figure and adjust whitespace for subplots.
    fig = plt.figure()
    fig.subplots_adjust(hspace=4)
    for i, extension_type in enumerate(('neither', 'min', 'max', 'both')):
        # Get the appropriate norm and use it to get colorbar boundaries.
        norm = norms[extension_type]
        boundaries = values = norm.boundaries
        # note that the last value was silently dropped pre 3.3:
        values = values[:-1]
        # Create a subplot.
        cax = fig.add_subplot(4, 1, i + 1)
        # Generate the colorbar.
        Colorbar(cax, cmap=cmap, norm=norm,
                 boundaries=boundaries, values=values,
                 extend=extension_type, extendrect=True,
                 orientation='horizontal', spacing=spacing)
        # Turn off text and ticks.
        cax.tick_params(left=False, labelleft=False,
                        bottom=False, labelbottom=False)
    # Return the figure to the caller.
    return fig


def _colorbar_extension_length(spacing):
    """
    Produce 12 colorbars with variable length extensions for either
    uniform or proportional spacing.

    Helper function for test_colorbar_extension_length.
    """
    # Get a colormap and appropriate norms for each extension type.
    cmap, norms = _get_cmap_norms()
    # Create a figure and adjust whitespace for subplots.
    fig = plt.figure()
    fig.subplots_adjust(hspace=.6)
    for i, extension_type in enumerate(('neither', 'min', 'max', 'both')):
        # Get the appropriate norm and use it to get colorbar boundaries.
        norm = norms[extension_type]
        boundaries = values = norm.boundaries
        values = values[:-1]
        for j, extendfrac in enumerate((None, 'auto', 0.1)):
            # Create a subplot.
            cax = fig.add_subplot(12, 1, i*3 + j + 1)
            # Generate the colorbar.
            Colorbar(cax, cmap=cmap, norm=norm,
                     boundaries=boundaries, values=values,
                     extend=extension_type, extendfrac=extendfrac,
                     orientation='horizontal', spacing=spacing)
            # Turn off text and ticks.
            cax.tick_params(left=False, labelleft=False,
                              bottom=False, labelbottom=False)
    # Return the figure to the caller.
    return fig


@image_comparison(['colorbar_extensions_shape_uniform.png',
                   'colorbar_extensions_shape_proportional.png'])
def test_colorbar_extension_shape():
    """Test rectangular colorbar extensions."""
    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    # Create figures for uniform and proportionally spaced colorbars.
    _colorbar_extension_shape('uniform')
    _colorbar_extension_shape('proportional')


@image_comparison(['colorbar_extensions_uniform.png',
                   'colorbar_extensions_proportional.png'],
                  tol=1.0)
def test_colorbar_extension_length():
    """Test variable length colorbar extensions."""
    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    # Create figures for uniform and proportionally spaced colorbars.
    _colorbar_extension_length('uniform')
    _colorbar_extension_length('proportional')


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
@pytest.mark.parametrize("extend,expected", [("min", (0, 0, 0, 1)),
                                             ("max", (1, 1, 1, 1)),
                                             ("both", (1, 1, 1, 1))])
def test_colorbar_extension_inverted_axis(orientation, extend, expected):
    """Test extension color with an inverted axis"""
    data = np.arange(12).reshape(3, 4)
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis").with_extremes(under=(0, 0, 0, 1),
                                                 over=(1, 1, 1, 1))
    im = ax.imshow(data, cmap=cmap)
    cbar = fig.colorbar(im, orientation=orientation, extend=extend)
    if orientation == "horizontal":
        cbar.ax.invert_xaxis()
    else:
        cbar.ax.invert_yaxis()
    assert cbar._extend_patches[0].get_facecolor() == expected
    if extend == "both":
        assert len(cbar._extend_patches) == 2
        assert cbar._extend_patches[1].get_facecolor() == (0, 0, 0, 1)
    else:
        assert len(cbar._extend_patches) == 1


@pytest.mark.parametrize('use_gridspec', [True, False])
@image_comparison(['cbar_with_orientation',
                   'cbar_locationing',
                   'double_cbar',
                   'cbar_sharing',
                   ],
                  extensions=['png'], remove_text=True,
                  savefig_kwarg={'dpi': 40})
def test_colorbar_positioning(use_gridspec):
    """
    Generates a series of plots with colorbars using Matplotlib.
    
    This function creates various plots with colorbars, demonstrating different
    positioning and usage scenarios. The plots include:
    
    - Contour plots with horizontal colorbars.
    - Contour plots with colorbars positioned at different locations ('left', 'right', 'top', 'bottom').
    - Contour plots with extended colorbars and hatched regions.
    - Subplots with colorbars aligned to specific axes.
    
    Parameters:
    """

    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    data = np.arange(1200).reshape(30, 40)
    levels = [0, 200, 400, 600, 800, 1000, 1200]

    # -------------------
    plt.figure()
    plt.contourf(data, levels=levels)
    plt.colorbar(orientation='horizontal', use_gridspec=use_gridspec)

    locations = ['left', 'right', 'top', 'bottom']
    plt.figure()
    for i, location in enumerate(locations):
        plt.subplot(2, 2, i + 1)
        plt.contourf(data, levels=levels)
        plt.colorbar(location=location, use_gridspec=use_gridspec)

    # -------------------
    plt.figure()
    # make some other data (random integers)
    data_2nd = np.array([[2, 3, 2, 3], [1.5, 2, 2, 3], [2, 3, 3, 4]])
    # make the random data expand to the shape of the main data
    data_2nd = np.repeat(np.repeat(data_2nd, 10, axis=1), 10, axis=0)

    color_mappable = plt.contourf(data, levels=levels, extend='both')
    # test extend frac here
    hatch_mappable = plt.contourf(data_2nd, levels=[1, 2, 3], colors='none',
                                  hatches=['/', 'o', '+'], extend='max')
    plt.contour(hatch_mappable, colors='black')

    plt.colorbar(color_mappable, location='left', label='variable 1',
                 use_gridspec=use_gridspec)
    plt.colorbar(hatch_mappable, location='right', label='variable 2',
                 use_gridspec=use_gridspec)

    # -------------------
    plt.figure()
    ax1 = plt.subplot(211, anchor='NE', aspect='equal')
    plt.contourf(data, levels=levels)
    ax2 = plt.subplot(223)
    plt.contourf(data, levels=levels)
    ax3 = plt.subplot(224)
    plt.contourf(data, levels=levels)

    plt.colorbar(ax=[ax2, ax3, ax1], location='right', pad=0.0, shrink=0.5,
                 panchor=False, use_gridspec=use_gridspec)
    plt.colorbar(ax=[ax2, ax3, ax1], location='left', shrink=0.5,
                 panchor=False, use_gridspec=use_gridspec)
    plt.colorbar(ax=[ax1], location='bottom', panchor=False,
                 anchor=(0.8, 0.5), shrink=0.6, use_gridspec=use_gridspec)


def test_colorbar_single_ax_panchor_false():
    """
    Create a colorbar for a single axes without using gridspec anchoring.
    
    This function generates a colorbar for an image displayed on a single axes
    without relying on gridspec anchoring. The primary function used here is
    `plt.imshow` to display the image and `plt.colorbar` to create the colorbar.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function does not return any value; it only creates a plot.
    -
    """

    # Just smoketesting that this doesn't crash.  Note that this differs from
    # the tests above with panchor=False because there use_gridspec is actually
    # ineffective: passing *ax* as lists always disable use_gridspec.
    plt.imshow([[0, 1]])
    plt.colorbar(panchor=False)


@image_comparison(['contour_colorbar.png'], remove_text=True)
def test_contour_colorbar():
    """
    Generates a contour plot with colorbars.
    
    This function creates a contour plot using the `contour` method from Matplotlib and adds two colorbars to the figure: one horizontal and one vertical. The contour plot is based on a 30x40 array of data values, with specified contour levels.
    
    Parameters:
    None
    
    Returns:
    fig (Figure): A Matplotlib Figure object containing the contour plot and colorbars.
    ax (Axes): A Matplotlib Axes
    """

    fig, ax = plt.subplots(figsize=(4, 2))
    data = np.arange(1200).reshape(30, 40) - 500
    levels = np.array([0, 200, 400, 600, 800, 1000, 1200]) - 500

    CS = ax.contour(data, levels=levels, extend='both')
    fig.colorbar(CS, orientation='horizontal', extend='both')
    fig.colorbar(CS, orientation='vertical')


@image_comparison(['cbar_with_subplots_adjust.png'], remove_text=True,
                  savefig_kwarg={'dpi': 40})
def test_gridspec_make_colorbar():
    """
    Generate a figure with two subplots containing contour plots and colorbars.
    
    This function creates a figure with two subplots. The first subplot displays
    a contour plot of a 30x40 array `data` with specified `levels`. A vertical
    colorbar is added to this subplot using `plt.colorbar()` with the
    `use_gridspec=True` option. The second subplot also displays a contour plot
    of the same `data` array with the same
    """

    plt.figure()
    data = np.arange(1200).reshape(30, 40)
    levels = [0, 200, 400, 600, 800, 1000, 1200]

    plt.subplot(121)
    plt.contourf(data, levels=levels)
    plt.colorbar(use_gridspec=True, orientation='vertical')

    plt.subplot(122)
    plt.contourf(data, levels=levels)
    plt.colorbar(use_gridspec=True, orientation='horizontal')

    plt.subplots_adjust(top=0.95, right=0.95, bottom=0.2, hspace=0.25)


@image_comparison(['colorbar_single_scatter.png'], remove_text=True,
                  savefig_kwarg={'dpi': 40})
def test_colorbar_single_scatter():
    """
    Generate a scatter plot with a single data point and create a colorbar.
    
    This function creates a scatter plot with a single data point at (0, 0) and
    assigns a color based on the value 50 using the 'jet' colormap with 16
    discrete levels. A colorbar is then added to the plot to represent the
    color mapping.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Issue #2642: if a path collection has only one entry,
    # the norm scaling within the colorbar must ensure a
    # finite range, otherwise a zero denominator will occur in _locate.
    plt.figure()
    x = y = [0]
    z = [50]
    cmap = plt.get_cmap('jet', 16)
    cs = plt.scatter(x, y, z, c=z, cmap=cmap)
    plt.colorbar(cs)


@pytest.mark.parametrize('use_gridspec', [False, True],
                         ids=['no gridspec', 'with gridspec'])
def test_remove_from_figure(use_gridspec):
    """
    Test `remove` with the specified ``use_gridspec`` setting
    """
    fig, ax = plt.subplots()
    sc = ax.scatter([1, 2], [3, 4], cmap="spring")
    sc.set_array(np.array([5, 6]))
    pre_position = ax.get_position()
    cb = fig.colorbar(sc, use_gridspec=use_gridspec)
    fig.subplots_adjust()
    cb.remove()
    fig.subplots_adjust()
    post_position = ax.get_position()
    assert (pre_position.get_points() == post_position.get_points()).all()


def test_remove_from_figure_cl():
    """
    Test `remove` with constrained_layout
    """
    fig, ax = plt.subplots(constrained_layout=True)
    sc = ax.scatter([1, 2], [3, 4], cmap="spring")
    sc.set_array(np.array([5, 6]))
    fig.draw_without_rendering()
    pre_position = ax.get_position()
    cb = fig.colorbar(sc)
    cb.remove()
    fig.draw_without_rendering()
    post_position = ax.get_position()
    np.testing.assert_allclose(pre_position.get_points(),
                               post_position.get_points())


def test_colorbarbase():
    """
    Create a colorbar base on the given axes.
    
    This function generates a colorbar on the specified axes using the provided colormap.
    
    Parameters:
    ax (matplotlib.axes.Axes): The axes object where the colorbar will be drawn.
    
    Returns:
    matplotlib.colorbar.Colorbar: A colorbar object representing the specified colormap.
    
    Example:
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> colorbar = test_colorbarbase(ax)
    >>> plt
    """

    # smoke test from #3805
    ax = plt.gca()
    Colorbar(ax, cmap=plt.cm.bone)


@image_comparison(['colorbar_closed_patch.png'], remove_text=True)
def test_colorbar_closed_patch():
    """
    Generates a figure with multiple subplots containing colorbars with different extension styles.
    
    This function creates a figure with five subplots arranged horizontally. Each subplot contains a colorbar with a pcolormesh plot underneath. The colorbars have different extension styles: 'both', 'both' with fractional extension, 'both' with rectangular extension, and 'neither'. The colorbar values are set to a range from 0 to 10 with 5 discrete levels. The color map used
    """

    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_axes([0.05, 0.85, 0.9, 0.1])
    ax2 = fig.add_axes([0.1, 0.65, 0.75, 0.1])
    ax3 = fig.add_axes([0.05, 0.45, 0.9, 0.1])
    ax4 = fig.add_axes([0.05, 0.25, 0.9, 0.1])
    ax5 = fig.add_axes([0.05, 0.05, 0.9, 0.1])

    cmap = cm.get_cmap("RdBu", lut=5)

    im = ax1.pcolormesh(np.linspace(0, 10, 16).reshape((4, 4)), cmap=cmap)

    # The use of a "values" kwarg here is unusual.  It works only
    # because it is matched to the data range in the image and to
    # the number of colors in the LUT.
    values = np.linspace(0, 10, 5)
    cbar_kw = dict(orientation='horizontal', values=values, ticks=[])

    # The wide line is to show that the closed path is being handled
    # correctly.  See PR #4186.
    with rc_context({'axes.linewidth': 16}):
        plt.colorbar(im, cax=ax2, extend='both', extendfrac=0.5, **cbar_kw)
        plt.colorbar(im, cax=ax3, extend='both', **cbar_kw)
        plt.colorbar(im, cax=ax4, extend='both', extendrect=True, **cbar_kw)
        plt.colorbar(im, cax=ax5, extend='neither', **cbar_kw)


def test_colorbar_ticks():
    """
    Test function for verifying the functionality of colorbar ticks in matplotlib.
    
    This function creates a contour plot with specified levels and colors, then
    adds a horizontal colorbar with custom ticks. The primary objective is to
    ensure that the number of tick locations on the colorbar matches the number
    of specified contour levels.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots()`: Creates a new figure and a set of subplots.
    """

    # test fix for #5673
    fig, ax = plt.subplots()
    x = np.arange(-3.0, 4.001)
    y = np.arange(-4.0, 3.001)
    X, Y = np.meshgrid(x, y)
    Z = X * Y
    clevs = np.array([-12, -5, 0, 5, 12], dtype=float)
    colors = ['r', 'g', 'b', 'c']
    cs = ax.contourf(X, Y, Z, clevs, colors=colors, extend='neither')
    cbar = fig.colorbar(cs, ax=ax, orientation='horizontal', ticks=clevs)
    assert len(cbar.ax.xaxis.get_ticklocs()) == len(clevs)


def test_colorbar_minorticks_on_off():
    """
    Test colorbar minorticks functionality.
    
    This function tests the behavior of minor ticks on a colorbar for different
    scenarios involving `pcolormesh` and `LogNorm`. It ensures that minor ticks
    are correctly turned on and off, and that their positions are as expected
    for given color limits.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `pcolormesh`: To create a pseudocolor plot from the input
    """

    # test for github issue #11510 and PR #11584
    np.random.seed(seed=12345)
    data = np.random.randn(20, 20)
    with rc_context({'_internal.classic_mode': False}):
        fig, ax = plt.subplots()
        # purposefully setting vmin and vmax to odd fractions
        # so as to check for the correct locations of the minor ticks
        im = ax.pcolormesh(data, vmin=-2.3, vmax=3.3)

        cbar = fig.colorbar(im, extend='both')
        # testing after minorticks_on()
        cbar.minorticks_on()
        np.testing.assert_almost_equal(
            cbar.ax.yaxis.get_minorticklocs(),
            [-2.2, -1.8, -1.6, -1.4, -1.2, -0.8, -0.6, -0.4, -0.2,
             0.2, 0.4, 0.6, 0.8, 1.2, 1.4, 1.6, 1.8, 2.2, 2.4, 2.6, 2.8, 3.2])
        # testing after minorticks_off()
        cbar.minorticks_off()
        np.testing.assert_almost_equal(cbar.ax.yaxis.get_minorticklocs(), [])

        im.set_clim(vmin=-1.2, vmax=1.2)
        cbar.minorticks_on()
        np.testing.assert_almost_equal(
            cbar.ax.yaxis.get_minorticklocs(),
            [-1.1, -0.9, -0.8, -0.7, -0.6, -0.4, -0.3, -0.2, -0.1,
             0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3])

    # tests for github issue #13257 and PR #13265
    data = np.random.uniform(low=1, high=10, size=(20, 20))

    fig, ax = plt.subplots()
    im = ax.pcolormesh(data, norm=LogNorm())
    cbar = fig.colorbar(im)
    fig.canvas.draw()
    default_minorticklocks = cbar.ax.yaxis.get_minorticklocs()
    # test that minorticks turn off for LogNorm
    cbar.minorticks_off()
    np.testing.assert_equal(cbar.ax.yaxis.get_minorticklocs(), [])

    # test that minorticks turn back on for LogNorm
    cbar.minorticks_on()
    np.testing.assert_equal(cbar.ax.yaxis.get_minorticklocs(),
                            default_minorticklocks)

    # test issue #13339: minorticks for LogNorm should stay off
    cbar.minorticks_off()
    cbar.set_ticks([3, 5, 7, 9])
    np.testing.assert_equal(cbar.ax.yaxis.get_minorticklocs(), [])


def test_cbar_minorticks_for_rc_xyminortickvisible():
    """
    issue gh-16468.

    Making sure that minor ticks on the colorbar are turned on
    (internally) using the cbar.minorticks_on() method when
    rcParams['xtick.minor.visible'] = True (for horizontal cbar)
    rcParams['ytick.minor.visible'] = True (for vertical cbar).
    Using cbar.minorticks_on() ensures that the minor ticks
    don't overflow into the extend regions of the colorbar.
    """

    plt.rcParams['ytick.minor.visible'] = True
    plt.rcParams['xtick.minor.visible'] = True

    vmin, vmax = 0.4, 2.6
    fig, ax = plt.subplots()
    im = ax.pcolormesh([[1, 2]], vmin=vmin, vmax=vmax)

    cbar = fig.colorbar(im, extend='both', orientation='vertical')
    assert cbar.ax.yaxis.get_minorticklocs()[0] >= vmin
    assert cbar.ax.yaxis.get_minorticklocs()[-1] <= vmax

    cbar = fig.colorbar(im, extend='both', orientation='horizontal')
    assert cbar.ax.xaxis.get_minorticklocs()[0] >= vmin
    assert cbar.ax.xaxis.get_minorticklocs()[-1] <= vmax


def test_colorbar_autoticks():
    """
    Test colorbar autotick modes.
    
    This function creates two subplots with pcolormesh plots and their respective colorbars. The colorbars are configured with different settings to test the autotick modes. The function asserts that the tick locations on the colorbars match expected values based on the given data range and settings.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `plt.subplots`: Creates a figure and a set of subplots.
    -
    """

    # Test new autotick modes. Needs to be classic because
    # non-classic doesn't go this route.
    with rc_context({'_internal.classic_mode': False}):
        fig, ax = plt.subplots(2, 1)
        x = np.arange(-3.0, 4.001)
        y = np.arange(-4.0, 3.001)
        X, Y = np.meshgrid(x, y)
        Z = X * Y
        Z = Z[:-1, :-1]
        pcm = ax[0].pcolormesh(X, Y, Z)
        cbar = fig.colorbar(pcm, ax=ax[0], extend='both',
                            orientation='vertical')

        pcm = ax[1].pcolormesh(X, Y, Z)
        cbar2 = fig.colorbar(pcm, ax=ax[1], extend='both',
                             orientation='vertical', shrink=0.4)
        # note only -10 to 10 are visible,
        np.testing.assert_almost_equal(cbar.ax.yaxis.get_ticklocs(),
                                       np.arange(-15, 16, 5))
        # note only -10 to 10 are visible
        np.testing.assert_almost_equal(cbar2.ax.yaxis.get_ticklocs(),
                                       np.arange(-20, 21, 10))


def test_colorbar_autotickslog():
    """
    Test automatic tick generation for colorbars with logarithmic normalization.
    
    This function creates two subplots with pcolormesh plots using logarithmic
    normalization. It then generates colorbars for these plots and asserts that
    the tick locations on the colorbars match expected values. The function uses
    `pcolormesh`, `LogNorm`, and `colorbar` from matplotlib to create the plots
    and colorbars. The key aspects of this function include:
    
    - Creating sub
    """

    # Test new autotick modes...
    with rc_context({'_internal.classic_mode': False}):
        fig, ax = plt.subplots(2, 1)
        x = np.arange(-3.0, 4.001)
        y = np.arange(-4.0, 3.001)
        X, Y = np.meshgrid(x, y)
        Z = X * Y
        Z = Z[:-1, :-1]
        pcm = ax[0].pcolormesh(X, Y, 10**Z, norm=LogNorm())
        cbar = fig.colorbar(pcm, ax=ax[0], extend='both',
                            orientation='vertical')

        pcm = ax[1].pcolormesh(X, Y, 10**Z, norm=LogNorm())
        cbar2 = fig.colorbar(pcm, ax=ax[1], extend='both',
                             orientation='vertical', shrink=0.4)
        # note only -12 to +12 are visible
        np.testing.assert_almost_equal(cbar.ax.yaxis.get_ticklocs(),
                                       10**np.arange(-16., 16.2, 4.))
        # note only -24 to +24 are visible
        np.testing.assert_almost_equal(cbar2.ax.yaxis.get_ticklocs(),
                                       10**np.arange(-24., 25., 12.))


def test_colorbar_get_ticks():
    """
    Test the functionality of colorbar tick retrieval and manipulation.
    
    This function tests various aspects of colorbar tick retrieval and manipulation,
    including setting custom ticks, retrieving default ticks, and handling ticks
    outside the range of the colorbar levels.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.contourf`: Creates a filled contour plot.
    - `plt.colorbar`: Adds a colorbar to the plot.
    - `userTicks.get_ticks
    """

    # test feature for #5792
    plt.figure()
    data = np.arange(1200).reshape(30, 40)
    levels = [0, 200, 400, 600, 800, 1000, 1200]

    plt.contourf(data, levels=levels)

    # testing getter for user set ticks
    userTicks = plt.colorbar(ticks=[0, 600, 1200])
    assert userTicks.get_ticks().tolist() == [0, 600, 1200]

    # testing for getter after calling set_ticks
    userTicks.set_ticks([600, 700, 800])
    assert userTicks.get_ticks().tolist() == [600, 700, 800]

    # testing for getter after calling set_ticks with some ticks out of bounds
    # removed #20054: other axes don't trim fixed lists, so colorbars
    # should not either:
    # userTicks.set_ticks([600, 1300, 1400, 1500])
    # assert userTicks.get_ticks().tolist() == [600]

    # testing getter when no ticks are assigned
    defTicks = plt.colorbar(orientation='horizontal')
    np.testing.assert_allclose(defTicks.get_ticks().tolist(), levels)

    # test normal ticks and minor ticks
    fig, ax = plt.subplots()
    x = np.arange(-3.0, 4.001)
    y = np.arange(-4.0, 3.001)
    X, Y = np.meshgrid(x, y)
    Z = X * Y
    Z = Z[:-1, :-1]
    pcm = ax.pcolormesh(X, Y, Z)
    cbar = fig.colorbar(pcm, ax=ax, extend='both',
                        orientation='vertical')
    ticks = cbar.get_ticks()
    np.testing.assert_allclose(ticks, np.arange(-15, 16, 5))
    assert len(cbar.get_ticks(minor=True)) == 0


@pytest.mark.parametrize("extend", ['both', 'min', 'max'])
def test_colorbar_lognorm_extension(extend):
    """
    Generate a colorbar with a logarithmic normalization.
    
    This function creates a colorbar using a logarithmic normalization
    with specified minimum and maximum values. The colorbar can be
    extended based on the provided `extend` parameter.
    
    Parameters:
    extend (str): Determines how the colorbar is extended. Options are 'both', 'min', 'max', or None.
    
    Returns:
    matplotlib.colorbar.Colorbar: A colorbar object with logarithmic normalization and optional extension.
    """

    # Test that colorbar with lognorm is extended correctly
    f, ax = plt.subplots()
    cb = Colorbar(ax, norm=LogNorm(vmin=0.1, vmax=1000.0),
                  orientation='vertical', extend=extend)
    assert cb._values[0] >= 0.0


def test_colorbar_powernorm_extension():
    """
    Generate a colorbar with a power normalization that extends both ends.
    
    This function creates a colorbar using the `Colorbar` class from matplotlib,
    with a `PowerNorm` normalization applied. The colorbar is configured to extend
    both ends of the color scale.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure containing the colorbar.
    ax (matplotlib.axes.Axes): The axes object containing the colorbar.
    
    Usage:
    """

    # Test that colorbar with powernorm is extended correctly
    f, ax = plt.subplots()
    cb = Colorbar(ax, norm=PowerNorm(gamma=0.5, vmin=0.0, vmax=1.0),
                  orientation='vertical', extend='both')
    assert cb._values[0] >= 0.0


def test_colorbar_axes_kw():
    """
    Test colorbar with various axes keyword arguments.
    
    This function creates a figure, displays an image using `imshow`, and adds a horizontal colorbar with specified axes-related keyword arguments. The function ensures that these keyword arguments are passed without raising any exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Keyword Arguments:
    - `fraction`: Fraction of original colorbar size (default: 0.2).
    - `pad`: Distance between the colorbar and the main plot
    """

    # test fix for #8493: This does only test, that axes-related keywords pass
    # and do not raise an exception.
    plt.figure()
    plt.imshow([[1, 2], [3, 4]])
    plt.colorbar(orientation='horizontal', fraction=0.2, pad=0.2, shrink=0.5,
                 aspect=10, anchor=(0., 0.), panchor=(0., 1.))


def test_colorbar_log_minortick_labels():
    """
    Generate a colorbar with logarithmic normalization and minor tick labels.
    
    This function creates a colorbar with logarithmic normalization and
    minor tick labels for an imshow plot. The function asserts that the
    generated tick labels match the expected values.
    
    Parameters:
    None
    
    Returns:
    None
    
    Usage:
    test_colorbar_log_minortick_labels()
    
    Important Functions:
    - `plt.subplots`: Creates a figure and a set of subplots.
    - `ax.imshow
    """

    with rc_context({'_internal.classic_mode': False}):
        fig, ax = plt.subplots()
        pcm = ax.imshow([[10000, 50000]], norm=LogNorm())
        cb = fig.colorbar(pcm)
        fig.canvas.draw()
        lb = [l.get_text() for l in cb.ax.yaxis.get_ticklabels(which='both')]
        expected = [r'$\mathdefault{10^{4}}$',
                    r'$\mathdefault{2\times10^{4}}$',
                    r'$\mathdefault{3\times10^{4}}$',
                    r'$\mathdefault{4\times10^{4}}$']
        for exp in expected:
            assert exp in lb


def test_colorbar_renorm():
    """
    Test colorbar renormalization.
    
    This function tests the behavior of colorbars when the normalization
    of an image is changed. It creates an image using `imshow` with data
    scaled by `exp(-x^2 - y^2)`. The colorbar is initially created without
    any normalization changes. Then, the normalization is updated to `LogNorm`
    with different scaling factors, and the colorbar ticks and limits are checked
    accordingly.
    
    Parameters:
    """

    x, y = np.ogrid[-4:4:31j, -4:4:31j]
    z = 120000*np.exp(-x**2 - y**2)

    fig, ax = plt.subplots()
    im = ax.imshow(z)
    cbar = fig.colorbar(im)
    np.testing.assert_allclose(cbar.ax.yaxis.get_majorticklocs(),
                               np.arange(0, 120000.1, 20000))

    cbar.set_ticks([1, 2, 3])
    assert isinstance(cbar.locator, FixedLocator)

    norm = LogNorm(z.min(), z.max())
    im.set_norm(norm)
    np.testing.assert_allclose(cbar.ax.yaxis.get_majorticklocs(),
                               np.logspace(-10, 7, 18))
    # note that set_norm removes the FixedLocator...
    assert np.isclose(cbar.vmin, z.min())
    cbar.set_ticks([1, 2, 3])
    assert isinstance(cbar.locator, FixedLocator)
    np.testing.assert_allclose(cbar.ax.yaxis.get_majorticklocs(),
                               [1.0, 2.0, 3.0])

    norm = LogNorm(z.min() * 1000, z.max() * 1000)
    im.set_norm(norm)
    assert np.isclose(cbar.vmin, z.min() * 1000)
    assert np.isclose(cbar.vmax, z.max() * 1000)


@pytest.mark.parametrize('fmt', ['%4.2e', '{x:.2e}'])
def test_colorbar_format(fmt):
    """
    Test the colorbar format function.
    
    This function tests the behavior of the colorbar format function by creating an image using imshow and adding a colorbar with the specified format. It then checks the tick labels on the colorbar to ensure they are formatted correctly according to the given format. The function also verifies that the formatting is preserved when the clim of the mappable is changed, but is updated when the norm is changed.
    
    Parameters:
    fmt (str): The format string to be used for
    """

    # make sure that format is passed properly
    x, y = np.ogrid[-4:4:31j, -4:4:31j]
    z = 120000*np.exp(-x**2 - y**2)

    fig, ax = plt.subplots()
    im = ax.imshow(z)
    cbar = fig.colorbar(im, format=fmt)
    fig.canvas.draw()
    assert cbar.ax.yaxis.get_ticklabels()[4].get_text() == '8.00e+04'

    # make sure that if we change the clim of the mappable that the
    # formatting is *not* lost:
    im.set_clim([4, 200])
    fig.canvas.draw()
    assert cbar.ax.yaxis.get_ticklabels()[4].get_text() == '2.00e+02'

    # but if we change the norm:
    im.set_norm(LogNorm(vmin=0.1, vmax=10))
    fig.canvas.draw()
    assert (cbar.ax.yaxis.get_ticklabels()[0].get_text() ==
            '$\\mathdefault{10^{\N{Minus Sign}2}}$')


def test_colorbar_scale_reset():
    """
    Reset colorbar scale after setting normalization.
    
    This function tests the behavior of a colorbar when its associated
    colormap's normalization is changed. It creates a pcolormesh plot with
    a red outline for the colorbar and checks that the scale of the colorbar
    changes correctly when the normalization is updated.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `np.ogrid`: Generates coordinate arrays for plotting.
    - `plt
    """

    x, y = np.ogrid[-4:4:31j, -4:4:31j]
    z = 120000*np.exp(-x**2 - y**2)

    fig, ax = plt.subplots()
    pcm = ax.pcolormesh(z, cmap='RdBu_r', rasterized=True)
    cbar = fig.colorbar(pcm, ax=ax)
    cbar.outline.set_edgecolor('red')
    assert cbar.ax.yaxis.get_scale() == 'linear'

    pcm.set_norm(LogNorm(vmin=1, vmax=100))
    assert cbar.ax.yaxis.get_scale() == 'log'
    pcm.set_norm(Normalize(vmin=-20, vmax=20))
    assert cbar.ax.yaxis.get_scale() == 'linear'

    assert cbar.outline.get_edgecolor() == mcolors.to_rgba('red')


def test_colorbar_get_ticks_2():
    """
    Generate a colorbar with specified ticks.
    
    This function creates a figure and axis object, plots a pcolormesh,
    and generates a colorbar with specific tick marks.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function sets the classic mode of matplotlib's rcParams to False.
    - A figure and axis are created using `plt.subplots()`.
    - A pcolormesh plot is generated with the data `[[.05,
    """

    plt.rcParams['_internal.classic_mode'] = False
    fig, ax = plt.subplots()
    pc = ax.pcolormesh([[.05, .95]])
    cb = fig.colorbar(pc)
    np.testing.assert_allclose(cb.get_ticks(), [0., 0.2, 0.4, 0.6, 0.8, 1.0])


def test_colorbar_inverted_ticks():
    """
    Test colorbar functionality with inverted y-axis.
    
    This function tests the behavior of colorbars with logarithmic normalization
    and minor ticks. It creates two subplots, each containing a pcolormesh plot
    with a corresponding colorbar. The colorbars are then manipulated by inverting
    the y-axis and checking if the ticks remain consistent before and after the
    inversion.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots
    """

    fig, axs = plt.subplots(2)
    ax = axs[0]
    pc = ax.pcolormesh(10**np.arange(1, 5).reshape(2, 2), norm=LogNorm())
    cbar = fig.colorbar(pc, ax=ax, extend='both')
    ticks = cbar.get_ticks()
    cbar.ax.invert_yaxis()
    np.testing.assert_allclose(ticks, cbar.get_ticks())

    ax = axs[1]
    pc = ax.pcolormesh(np.arange(1, 5).reshape(2, 2))
    cbar = fig.colorbar(pc, ax=ax, extend='both')
    cbar.minorticks_on()
    ticks = cbar.get_ticks()
    minorticks = cbar.get_ticks(minor=True)
    assert isinstance(minorticks, np.ndarray)
    cbar.ax.invert_yaxis()
    np.testing.assert_allclose(ticks, cbar.get_ticks())
    np.testing.assert_allclose(minorticks, cbar.get_ticks(minor=True))


def test_mappable_no_alpha():
    """
    Generate a colorbar with a ScalarMappable object.
    
    This function creates a figure and axis using `plt.subplots`, initializes a
    `ScalarMappable` object with a `Normalize` normalization and 'viridis' colormap,
    adds a colorbar to the plot, changes the colormap to 'plasma', and draws the
    figure.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The created figure object.
    ax (matplotlib.axes.Axes
    """

    fig, ax = plt.subplots()
    sm = cm.ScalarMappable(norm=mcolors.Normalize(), cmap='viridis')
    fig.colorbar(sm)
    sm.set_cmap('plasma')
    plt.draw()


def test_mappable_2d_alpha():
    """
    Generate a pcolormesh plot with varying alpha values and ensure that the colorbar's alpha is set to None while preserving the original alpha array for the mappable.
    
    Parameters:
    None
    
    Returns:
    None
    
    Summary:
    This function creates a 2D pcolormesh plot using `pcolormesh` from matplotlib.pyplot with an array `x` where each element has a corresponding alpha value. It then generates a colorbar for this plot using `colorbar
    """

    fig, ax = plt.subplots()
    x = np.arange(1, 5).reshape(2, 2)/4
    pc = ax.pcolormesh(x, alpha=x)
    cb = fig.colorbar(pc, ax=ax)
    # The colorbar's alpha should be None and the mappable should still have
    # the original alpha array
    assert cb.alpha is None
    assert pc.get_alpha() is x
    fig.draw_without_rendering()


def test_colorbar_label():
    """
    Test the label parameter. It should just be mapped to the xlabel/ylabel of
    the axes, depending on the orientation.
    """
    fig, ax = plt.subplots()
    im = ax.imshow([[1, 2], [3, 4]])
    cbar = fig.colorbar(im, label='cbar')
    assert cbar.ax.get_ylabel() == 'cbar'
    cbar.set_label(None)
    assert cbar.ax.get_ylabel() == ''
    cbar.set_label('cbar 2')
    assert cbar.ax.get_ylabel() == 'cbar 2'

    cbar2 = fig.colorbar(im, label=None)
    assert cbar2.ax.get_ylabel() == ''

    cbar3 = fig.colorbar(im, orientation='horizontal', label='horizontal cbar')
    assert cbar3.ax.get_xlabel() == 'horizontal cbar'


@pytest.mark.parametrize("clim", [(-20000, 20000), (-32768, 0)])
def test_colorbar_int(clim):
    """
    Generate a colorbar for an image with specified clim.
    
    Parameters:
    -----------
    clim : tuple of two integers
    The minimum and maximum values for the colorbar.
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
    The figure containing the colorbar.
    ax : matplotlib.axes.Axes
    The axes containing the image.
    im : matplotlib.image.AxesImage
    The image object.
    
    Notes:
    ------
    This function creates a figure with a
    """

    # Check that we cast to float early enough to not
    # overflow ``int16(20000) - int16(-20000)`` or
    # run into ``abs(int16(-32768)) == -32768``.
    fig, ax = plt.subplots()
    im = ax.imshow([[*map(np.int16, clim)]])
    fig.colorbar(im)
    assert (im.norm.vmin, im.norm.vmax) == clim


def test_anchored_cbar_position_using_specgrid():
    """
    Test the positioning of colorbars anchored at specific locations using `GridSpec`.
    
    This function tests the placement of colorbars (`cbar`) on a contour plot (`contourf`)
    with specified anchor points and shrink factors. The colorbars are positioned either
    to the 'right', 'left', 'top', or 'bottom' of the contour plot.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots()`: Creates a new
    """

    data = np.arange(1200).reshape(30, 40)
    levels = [0, 200, 400, 600, 800, 1000, 1200]
    shrink = 0.5
    anchor_y = 0.3
    # right
    fig, ax = plt.subplots()
    cs = ax.contourf(data, levels=levels)
    cbar = plt.colorbar(
            cs, ax=ax, use_gridspec=True,
            location='right', anchor=(1, anchor_y), shrink=shrink)

    # the bottom left corner of one ax is (x0, y0)
    # the top right corner of one ax is (x1, y1)
    # p0: the vertical / horizontal position of anchor
    x0, y0, x1, y1 = ax.get_position().extents
    cx0, cy0, cx1, cy1 = cbar.ax.get_position().extents
    p0 = (y1 - y0) * anchor_y + y0

    np.testing.assert_allclose(
            [cy1, cy0],
            [y1 * shrink + (1 - shrink) * p0, p0 * (1 - shrink) + y0 * shrink])

    # left
    fig, ax = plt.subplots()
    cs = ax.contourf(data, levels=levels)
    cbar = plt.colorbar(
            cs, ax=ax, use_gridspec=True,
            location='left', anchor=(1, anchor_y), shrink=shrink)

    # the bottom left corner of one ax is (x0, y0)
    # the top right corner of one ax is (x1, y1)
    # p0: the vertical / horizontal position of anchor
    x0, y0, x1, y1 = ax.get_position().extents
    cx0, cy0, cx1, cy1 = cbar.ax.get_position().extents
    p0 = (y1 - y0) * anchor_y + y0

    np.testing.assert_allclose(
            [cy1, cy0],
            [y1 * shrink + (1 - shrink) * p0, p0 * (1 - shrink) + y0 * shrink])

    # top
    shrink = 0.5
    anchor_x = 0.3
    fig, ax = plt.subplots()
    cs = ax.contourf(data, levels=levels)
    cbar = plt.colorbar(
            cs, ax=ax, use_gridspec=True,
            location='top', anchor=(anchor_x, 1), shrink=shrink)

    # the bottom left corner of one ax is (x0, y0)
    # the top right corner of one ax is (x1, y1)
    # p0: the vertical / horizontal position of anchor
    x0, y0, x1, y1 = ax.get_position().extents
    cx0, cy0, cx1, cy1 = cbar.ax.get_position().extents
    p0 = (x1 - x0) * anchor_x + x0

    np.testing.assert_allclose(
            [cx1, cx0],
            [x1 * shrink + (1 - shrink) * p0, p0 * (1 - shrink) + x0 * shrink])

    # bottom
    shrink = 0.5
    anchor_x = 0.3
    fig, ax = plt.subplots()
    cs = ax.contourf(data, levels=levels)
    cbar = plt.colorbar(
            cs, ax=ax, use_gridspec=True,
            location='bottom', anchor=(anchor_x, 1), shrink=shrink)

    # the bottom left corner of one ax is (x0, y0)
    # the top right corner of one ax is (x1, y1)
    # p0: the vertical / horizontal position of anchor
    x0, y0, x1, y1 = ax.get_position().extents
    cx0, cy0, cx1, cy1 = cbar.ax.get_position().extents
    p0 = (x1 - x0) * anchor_x + x0

    np.testing.assert_allclose(
            [cx1, cx0],
            [x1 * shrink + (1 - shrink) * p0, p0 * (1 - shrink) + x0 * shrink])


@image_comparison(['colorbar_change_lim_scale.png'], remove_text=True,
                  style='mpl20')
def test_colorbar_change_lim_scale():
    """
    Adjust colorbar limits and scale in subplots.
    
    This function creates two subplots with pcolormesh plots and adjusts the
    colorbar limits and scale for each subplot. The first subplot sets the
    colorbar scale to logarithmic, while the second subplot sets the colorbar
    limits to a specific range.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure containing the subplots.
    ax (list of matplotlib.axes.Axes
    """

    fig, ax = plt.subplots(1, 2, constrained_layout=True)
    pc = ax[0].pcolormesh(np.arange(100).reshape(10, 10)+1)
    cb = fig.colorbar(pc, ax=ax[0], extend='both')
    cb.ax.set_yscale('log')

    pc = ax[1].pcolormesh(np.arange(100).reshape(10, 10)+1)
    cb = fig.colorbar(pc, ax=ax[1], extend='both')
    cb.ax.set_ylim([20, 90])


@check_figures_equal(extensions=["png"])
def test_axes_handles_same_functions(fig_ref, fig_test):
    """
    Test whether the colorbar axes (cax) and the colorbar's own axes (cb.ax) handle the same functions.
    
    This function compares two figures (fig_ref and fig_test) to verify that the colorbar axes (cax) and the colorbar's own axes (cb.ax) behave identically when setting y-ticks, y-scale, and position.
    
    Parameters:
    fig_ref (matplotlib.figure.Figure): The reference figure for comparison.
    fig_test (matplotlib.figure
    """

    # prove that cax and cb.ax are functionally the same
    for nn, fig in enumerate([fig_ref, fig_test]):
        ax = fig.add_subplot()
        pc = ax.pcolormesh(np.ones(300).reshape(10, 30))
        cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
        cb = fig.colorbar(pc, cax=cax)
        if nn == 0:
            caxx = cax
        else:
            caxx = cb.ax
        caxx.set_yticks(np.arange(0, 20))
        caxx.set_yscale('log')
        caxx.set_position([0.92, 0.1, 0.02, 0.7])


def test_inset_colorbar_layout():
    """
    Inserts a colorbar into a subplot with specified layout parameters.
    
    This function creates a figure and a constrained subplot, then adds an
    image to the subplot using imshow. A colorbar is inserted adjacent to the
    image using inset_axes. The function ensures that the colorbar is correctly
    positioned and included in the subplot's child axes.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The created figure object.
    ax (matplotlib.axes.A
    """

    fig, ax = plt.subplots(constrained_layout=True, figsize=(3, 6))
    pc = ax.imshow(np.arange(100).reshape(10, 10))
    cax = ax.inset_axes([1.02, 0.1, 0.03, 0.8])
    cb = fig.colorbar(pc, cax=cax)

    fig.draw_without_rendering()
    # make sure this is in the figure. In the colorbar swapping
    # it was being dropped from the list of children...
    np.testing.assert_allclose(cb.ax.get_position().bounds,
                               [0.87, 0.342, 0.0237, 0.315], atol=0.01)
    assert cb.ax in ax.child_axes


@image_comparison(['colorbar_twoslope.png'], remove_text=True,
                  style='mpl20')
def test_twoslope_colorbar():
    """
    Generate a two-slope colorbar with specified normalization.
    
    This function creates a pcolor mesh plot with a custom colormap and
    normalization. The colorbar has two distinct slopes around a central value,
    with ticks placed appropriately based on the given normalization values.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the plot.
    ax (matplotlib.axes.Axes): The axes object containing the plot.
    
    Notes:
    - The second tick
    """

    # Note that the second tick = 20, and should be in the middle
    # of the colorbar (white)
    # There should be no tick right at the bottom, nor at the top.
    fig, ax = plt.subplots()

    norm = mcolors.TwoSlopeNorm(20, 5, 95)
    pc = ax.pcolormesh(np.arange(1, 11), np.arange(1, 11),
                       np.arange(100).reshape(10, 10),
                       norm=norm, cmap='RdBu_r')
    fig.colorbar(pc)


@check_figures_equal(extensions=["png"])
def test_remove_cb_whose_mappable_has_no_figure(fig_ref, fig_test):
    """
    Remove a colorbar (cb) from a figure (fig_test) whose mappable has no associated figure (fig_ref).
    
    Args:
    fig_ref (matplotlib.figure.Figure): The reference figure that the mappable should be associated with.
    fig_test (matplotlib.figure.Figure): The figure containing the colorbar to be removed.
    
    Returns:
    None: The function modifies the figure in place and does not return any value.
    """

    ax = fig_test.add_subplot()
    cb = fig_test.colorbar(cm.ScalarMappable(), cax=ax)
    cb.remove()


def test_aspects():
    """
    Generate colorbars with specified aspects and extensions.
    
    This function creates a figure with subplots containing pcolor meshes and
    corresponding colorbars. The colorbars have different aspects and extensions
    to demonstrate their behavior. The function checks that the colorbars have
    the correct aspect ratios and extensions.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): A matplotlib figure object containing the
    subplots and colorbars.
    
    Functions Used:
    - `plt
    """

    fig, ax = plt.subplots(3, 2, figsize=(8, 8))
    aspects = [20, 20, 10]
    extends = ['neither', 'both', 'both']
    cb = [[None, None, None], [None, None, None]]
    for nn, orient in enumerate(['vertical', 'horizontal']):
        for mm, (aspect, extend) in enumerate(zip(aspects, extends)):
            pc = ax[mm, nn].pcolormesh(np.arange(100).reshape(10, 10))
            cb[nn][mm] = fig.colorbar(pc, ax=ax[mm, nn], orientation=orient,
                                      aspect=aspect, extend=extend)
    fig.draw_without_rendering()
    # check the extends are right ratio:
    np.testing.assert_almost_equal(cb[0][1].ax.get_position().height,
                                   cb[0][0].ax.get_position().height * 0.9,
                                   decimal=2)
    # horizontal
    np.testing.assert_almost_equal(cb[1][1].ax.get_position().width,
                                   cb[1][0].ax.get_position().width * 0.9,
                                   decimal=2)
    # check correct aspect:
    pos = cb[0][0].ax.get_position(original=False)
    np.testing.assert_almost_equal(pos.height, pos.width * 20, decimal=2)
    pos = cb[1][0].ax.get_position(original=False)
    np.testing.assert_almost_equal(pos.height * 20, pos.width, decimal=2)
    # check twice as wide if aspect is 10 instead of 20
    np.testing.assert_almost_equal(
        cb[0][0].ax.get_position(original=False).width * 2,
        cb[0][2].ax.get_position(original=False).width, decimal=2)
    np.testing.assert_almost_equal(
        cb[1][0].ax.get_position(original=False).height * 2,
        cb[1][2].ax.get_position(original=False).height, decimal=2)


@image_comparison(['proportional_colorbars.png'], remove_text=True,
                  style='mpl20')
def test_proportional_colorbars():
    """
    Generates a set of contour plots with proportional colorbars.
    
    This function creates a grid of contour plots using the `contourf` method
    from matplotlib's `pyplot` module. Each plot uses a custom colormap defined
    by `ListedColormap`, with specific under and over colors. The colorbar for
    each plot is adjusted to have either uniform or proportional spacing based
    on the `spacing` parameter.
    
    Parameters:
    None
    
    Returns:
    """


    x = y = np.arange(-3.0, 3.01, 0.025)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = (Z1 - Z2) * 2

    levels = [-1.25, -0.5, -0.125, 0.125, 0.5, 1.25]
    cmap = mcolors.ListedColormap(
        ['0.3', '0.5', 'white', 'lightblue', 'steelblue'])
    cmap.set_under('darkred')
    cmap.set_over('crimson')
    norm = mcolors.BoundaryNorm(levels, cmap.N)

    extends = ['neither', 'both']
    spacings = ['uniform', 'proportional']
    fig, axs = plt.subplots(2, 2)
    for i in range(2):
        for j in range(2):
            CS3 = axs[i, j].contourf(X, Y, Z, levels, cmap=cmap, norm=norm,
                                     extend=extends[i])
            fig.colorbar(CS3, spacing=spacings[j], ax=axs[i, j])


def test_negative_boundarynorm():
    """
    Test the functionality of `BoundaryNorm` with different range of levels for colorbar.
    
    This function creates subplots and colorbars using `matplotlib` and `numpy`. It sets up a colormap (`viridis`) and uses `BoundaryNorm` to define the color boundaries. The function then checks if the colorbar's y-axis limits and ticks match the specified levels.
    
    Parameters:
    None
    
    Returns:
    None
    """

    fig, ax = plt.subplots(figsize=(1, 3))
    cmap = plt.get_cmap("viridis")

    clevs = np.arange(-94, -85)
    norm = BoundaryNorm(clevs, cmap.N)
    cb = fig.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), cax=ax)
    np.testing.assert_allclose(cb.ax.get_ylim(), [clevs[0], clevs[-1]])
    np.testing.assert_allclose(cb.ax.get_yticks(), clevs)

    clevs = np.arange(85, 94)
    norm = BoundaryNorm(clevs, cmap.N)
    cb = fig.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), cax=ax)
    np.testing.assert_allclose(cb.ax.get_ylim(), [clevs[0], clevs[-1]])
    np.testing.assert_allclose(cb.ax.get_yticks(), clevs)

    clevs = np.arange(-3, 3)
    norm = BoundaryNorm(clevs, cmap.N)
    cb = fig.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), cax=ax)
    np.testing.assert_allclose(cb.ax.get_ylim(), [clevs[0], clevs[-1]])
    np.testing.assert_allclose(cb.ax.get_yticks(), clevs)

    clevs = np.arange(-8, 1)
    norm = BoundaryNorm(clevs, cmap.N)
    cb = fig.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), cax=ax)
    np.testing.assert_allclose(cb.ax.get_ylim(), [clevs[0], clevs[-1]])
    np.testing.assert_allclose(cb.ax.get_yticks(), clevs)


@image_comparison(['nonorm_colorbars.svg'], remove_text=False,
                  style='mpl20')
def test_nonorm():
    """
    Generate a horizontal colorbar with non-normalized data.
    
    This function creates a horizontal colorbar using non-normalized data
    from a given list of values. The colorbar is generated using the 'viridis'
    colormap and does not apply any normalization to the data.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure containing the colorbar.
    ax (matplotlib.axes.Axes): The axes object containing the colorbar.
    
    Usage:
    """

    plt.rcParams['svg.fonttype'] = 'none'
    data = [1, 2, 3, 4, 5]

    fig, ax = plt.subplots(figsize=(6, 1))
    fig.subplots_adjust(bottom=0.5)

    norm = NoNorm(vmin=min(data), vmax=max(data))
    cmap = cm.get_cmap("viridis", len(data))
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(mappable, cax=ax, orientation="horizontal")


@image_comparison(['test_boundaries.png'], remove_text=True,
                  style='mpl20')
def test_boundaries():
    """
    Generate a pcolormesh plot with colorbar boundaries.
    
    This function creates a pcolormesh plot using random data and displays
    a colorbar with specified boundaries. The plot is constrained to a 2x2
    figure size.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The generated figure object.
    ax (matplotlib.axes.Axes): The axes object containing the plot.
    
    Usage:
    fig, ax = test_boundaries()
    """

    np.random.seed(seed=19680808)
    fig, ax = plt.subplots(figsize=(2, 2))
    pc = ax.pcolormesh(np.random.randn(10, 10), cmap='RdBu_r')
    cb = fig.colorbar(pc, ax=ax, boundaries=np.linspace(-3, 3, 7))


def test_colorbar_no_warning_rcparams_grid_true():
    """
    Generate a colorbar without raising a warning when axes.grid is set to True.
    
    This function sets the 'axes.grid' parameter in Matplotlib's rcParams to
    True, creates a figure and an axis, disables the grid on the axis using
    `ax.grid(False)`, and then plots a pseudocolor mesh using `ax.pcolormesh`.
    The primary purpose is to ensure that calling `fig.colorbar` does not raise
    a warning about auto-removal
    """

    # github issue #21723 - If mpl style has 'axes.grid' = True,
    # fig.colorbar raises a warning about Auto-removal of grids
    # by pcolor() and pcolormesh(). This is fixed by PR #22216.
    plt.rcParams['axes.grid'] = True
    fig, ax = plt.subplots()
    ax.grid(False)
    im = ax.pcolormesh([0, 1], [0, 1], [[1]])
    # make sure that no warning is raised by fig.colorbar
    fig.colorbar(im)


def test_colorbar_set_formatter_locator():
    """
    Set and verify colorbar formatters and locators.
    
    This function tests the setting of major and minor locators and formatters
    for a colorbar associated with a pcolormesh plot. It ensures that the
    specified locators and formatters are correctly applied to the colorbar's
    y-axis and that the setter methods work as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots()`: Creates a figure
    """

    # check that the locator properties echo what is on the axis:
    fig, ax = plt.subplots()
    pc = ax.pcolormesh(np.random.randn(10, 10))
    cb = fig.colorbar(pc)
    cb.ax.yaxis.set_major_locator(FixedLocator(np.arange(10)))
    cb.ax.yaxis.set_minor_locator(FixedLocator(np.arange(0, 10, 0.2)))
    assert cb.locator is cb.ax.yaxis.get_major_locator()
    assert cb.minorlocator is cb.ax.yaxis.get_minor_locator()
    cb.ax.yaxis.set_major_formatter(LogFormatter())
    cb.ax.yaxis.set_minor_formatter(LogFormatter())
    assert cb.formatter is cb.ax.yaxis.get_major_formatter()
    assert cb.minorformatter is cb.ax.yaxis.get_minor_formatter()

    # check that the setter works as expected:
    loc = FixedLocator(np.arange(7))
    cb.locator = loc
    assert cb.ax.yaxis.get_major_locator() is loc
    loc = FixedLocator(np.arange(0, 7, 0.1))
    cb.minorlocator = loc
    assert cb.ax.yaxis.get_minor_locator() is loc
    fmt = LogFormatter()
    cb.formatter = fmt
    assert cb.ax.yaxis.get_major_formatter() is fmt
    fmt = LogFormatter()
    cb.minorformatter = fmt
    assert cb.ax.yaxis.get_minor_formatter() is fmt


def test_offset_text_loc():
    """
    Test the position of the offset text in a colorbar.
    
    This function checks if the offset text in the colorbar is positioned correctly above the colorbar axes. It uses `pcolormesh` to create a mesh with random data scaled by a large factor, and `colorbar` to add a colorbar to the plot. The function then asserts that the offset text's y-position is greater than the bottom edge of the parent axes.
    
    Parameters:
    None
    
    Returns:
    """

    plt.style.use('mpl20')
    fig, ax = plt.subplots()
    np.random.seed(seed=19680808)
    pc = ax.pcolormesh(np.random.randn(10, 10)*1e6)
    cb = fig.colorbar(pc, location='right', extend='max')
    fig.draw_without_rendering()
    # check that the offsetText is in the proper place above the
    # colorbar axes.  In this case the colorbar axes is the same
    # height as the parent, so use the parents bbox.
    assert cb.ax.yaxis.offsetText.get_position()[1] > ax.bbox.y1


def test_title_text_loc():
    """
    Generate a colorbar with a title and verify the title's position relative to the colorbar.
    
    This function creates a pcolor mesh plot using `pcolormesh` and a colorbar with a specified title 'Aardvark'. It then checks if the title of the colorbar is positioned correctly above the colorbar's outline, ensuring that the title extends beyond the colorbar's bounding box.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    -
    """

    plt.style.use('mpl20')
    fig, ax = plt.subplots()
    np.random.seed(seed=19680808)
    pc = ax.pcolormesh(np.random.randn(10, 10))
    cb = fig.colorbar(pc, location='right', extend='max')
    cb.ax.set_title('Aardvark')
    fig.draw_without_rendering()
    # check that the title is in the proper place above the
    # colorbar axes, including its extend triangles....
    assert (cb.ax.title.get_window_extent(fig.canvas.get_renderer()).ymax >
            cb.ax.spines['outline'].get_window_extent().ymax)
