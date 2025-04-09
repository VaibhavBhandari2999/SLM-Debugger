import warnings

import numpy as np
from numpy.testing import assert_array_equal
import pytest

import matplotlib as mpl
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea
from matplotlib.patches import Rectangle


def example_plot(ax, fontsize=12):
    """
    Plots a line graph on the given axes object.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
    The axes object on which to plot the graph.
    
    fontsize : int, optional
    The font size for the labels and title (default is 12).
    
    Returns
    -------
    None
    
    This function plots a line graph with specified axes, adjusts the number of bins for the locator, and sets the labels and title with the given font size.
    """

    ax.plot([1, 2])
    ax.locator_params(nbins=3)
    ax.set_xlabel('x-label', fontsize=fontsize)
    ax.set_ylabel('y-label', fontsize=fontsize)
    ax.set_title('Title', fontsize=fontsize)


@image_comparison(['tight_layout1'], tol=1.9)
def test_tight_layout1():
    """Test tight_layout for a single subplot."""
    fig, ax = plt.subplots()
    example_plot(ax, fontsize=24)
    plt.tight_layout()


@image_comparison(['tight_layout2'])
def test_tight_layout2():
    """Test tight_layout for multiple subplots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
    example_plot(ax1)
    example_plot(ax2)
    example_plot(ax3)
    example_plot(ax4)
    plt.tight_layout()


@image_comparison(['tight_layout3'])
def test_tight_layout3():
    """Test tight_layout for multiple subplots."""
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(223)
    ax3 = plt.subplot(122)
    example_plot(ax1)
    example_plot(ax2)
    example_plot(ax3)
    plt.tight_layout()


@image_comparison(['tight_layout4'], freetype_version=('2.5.5', '2.6.1'),
                  tol=0.015)
def test_tight_layout4():
    """Test tight_layout for subplot2grid."""
    ax1 = plt.subplot2grid((3, 3), (0, 0))
    ax2 = plt.subplot2grid((3, 3), (0, 1), colspan=2)
    ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
    example_plot(ax1)
    example_plot(ax2)
    example_plot(ax3)
    example_plot(ax4)
    plt.tight_layout()


@image_comparison(['tight_layout5'])
def test_tight_layout5():
    """Test tight_layout for image."""
    ax = plt.subplot()
    arr = np.arange(100).reshape((10, 10))
    ax.imshow(arr, interpolation="none")
    plt.tight_layout()


@image_comparison(['tight_layout6'])
def test_tight_layout6():
    """Test tight_layout for gridspec."""

    # This raises warnings since tight layout cannot
    # do this fully automatically. But the test is
    # correct since the layout is manually edited
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        fig = plt.figure()

        gs1 = mpl.gridspec.GridSpec(2, 1)
        ax1 = fig.add_subplot(gs1[0])
        ax2 = fig.add_subplot(gs1[1])

        example_plot(ax1)
        example_plot(ax2)

        gs1.tight_layout(fig, rect=[0, 0, 0.5, 1])

        gs2 = mpl.gridspec.GridSpec(3, 1)

        for ss in gs2:
            ax = fig.add_subplot(ss)
            example_plot(ax)
            ax.set_title("")
            ax.set_xlabel("")

        ax.set_xlabel("x-label", fontsize=12)

        gs2.tight_layout(fig, rect=[0.5, 0, 1, 1], h_pad=0.45)

        top = min(gs1.top, gs2.top)
        bottom = max(gs1.bottom, gs2.bottom)

        gs1.tight_layout(fig, rect=[None, 0 + (bottom-gs1.bottom),
                                    0.5, 1 - (gs1.top-top)])
        gs2.tight_layout(fig, rect=[0.5, 0 + (bottom-gs2.bottom),
                                    None, 1 - (gs2.top-top)],
                         h_pad=0.45)


@image_comparison(['tight_layout7'], tol=1.9)
def test_tight_layout7():
    """
    Adjust subplot parameters to give specified padding while using left and right titles.
    
    Parameters:
    None
    
    Returns:
    fig (Figure): The created figure object.
    ax (Axes): The created axes object.
    
    Usage:
    fig, ax = test_tight_layout7()
    
    This function creates a plot with a left and right title using `set_title` with the 'loc' parameter set to 'left' and 'right'. It then applies `tight_layout` to adjust subplot parameters
    """

    # tight layout with left and right titles
    fontsize = 24
    fig, ax = plt.subplots()
    ax.plot([1, 2])
    ax.locator_params(nbins=3)
    ax.set_xlabel('x-label', fontsize=fontsize)
    ax.set_ylabel('y-label', fontsize=fontsize)
    ax.set_title('Left Title', loc='left', fontsize=fontsize)
    ax.set_title('Right Title', loc='right', fontsize=fontsize)
    plt.tight_layout()


@image_comparison(['tight_layout8'])
def test_tight_layout8():
    """Test automatic use of tight_layout."""
    fig = plt.figure()
    fig.set_layout_engine(layout='tight', pad=0.1)
    ax = fig.add_subplot()
    example_plot(ax, fontsize=24)
    fig.draw_without_rendering()


@image_comparison(['tight_layout9'])
def test_tight_layout9():
    """
    Test tight_layout functionality for non-visible subplots.
    
    This function creates a 2x2 grid of subplots using `plt.subplots`. It then
    sets the visibility of the bottom-right subplot to False, effectively making
    it invisible. The `tight_layout` method is called to adjust the spacing
    between subplots. The primary purpose of this test is to ensure that
    `tight_layout` correctly handles non-visible subplots without causing
    layout issues.
    
    Parameters:
    """

    # Test tight_layout for non-visible subplots
    # GH 8244
    f, axarr = plt.subplots(2, 2)
    axarr[1][1].set_visible(False)
    plt.tight_layout()


def test_outward_ticks():
    """Test automatic use of tight_layout."""
    fig = plt.figure()
    ax = fig.add_subplot(221)
    ax.xaxis.set_tick_params(tickdir='out', length=16, width=3)
    ax.yaxis.set_tick_params(tickdir='out', length=16, width=3)
    ax.xaxis.set_tick_params(
        tickdir='out', length=32, width=3, tick1On=True, which='minor')
    ax.yaxis.set_tick_params(
        tickdir='out', length=32, width=3, tick1On=True, which='minor')
    ax.xaxis.set_ticks([0], minor=True)
    ax.yaxis.set_ticks([0], minor=True)
    ax = fig.add_subplot(222)
    ax.xaxis.set_tick_params(tickdir='in', length=32, width=3)
    ax.yaxis.set_tick_params(tickdir='in', length=32, width=3)
    ax = fig.add_subplot(223)
    ax.xaxis.set_tick_params(tickdir='inout', length=32, width=3)
    ax.yaxis.set_tick_params(tickdir='inout', length=32, width=3)
    ax = fig.add_subplot(224)
    ax.xaxis.set_tick_params(tickdir='out', length=32, width=3)
    ax.yaxis.set_tick_params(tickdir='out', length=32, width=3)
    plt.tight_layout()
    # These values were obtained after visual checking that they correspond
    # to a tight layouting that did take the ticks into account.
    ans = [[[0.091, 0.607], [0.433, 0.933]],
           [[0.579, 0.607], [0.922, 0.933]],
           [[0.091, 0.140], [0.433, 0.466]],
           [[0.579, 0.140], [0.922, 0.466]]]
    for nn, ax in enumerate(fig.axes):
        assert_array_equal(np.round(ax.get_position().get_points(), 3),
                           ans[nn])


def add_offsetboxes(ax, size=10, margin=.1, color='black'):
    """
    Surround ax with OffsetBoxes
    """
    m, mp = margin, 1+margin
    anchor_points = [(-m, -m), (-m, .5), (-m, mp),
                     (mp, .5), (.5, mp), (mp, mp),
                     (.5, -m), (mp, -m), (.5, -m)]
    for point in anchor_points:
        da = DrawingArea(size, size)
        background = Rectangle((0, 0), width=size,
                               height=size,
                               facecolor=color,
                               edgecolor='None',
                               linewidth=0,
                               antialiased=False)
        da.add_artist(background)

        anchored_box = AnchoredOffsetbox(
            loc='center',
            child=da,
            pad=0.,
            frameon=False,
            bbox_to_anchor=point,
            bbox_transform=ax.transAxes,
            borderpad=0.)
        ax.add_artist(anchored_box)
    return anchored_box


@image_comparison(['tight_layout_offsetboxes1', 'tight_layout_offsetboxes2'])
def test_tight_layout_offsetboxes():
    """
    Test the functionality of `tight_layout` with `OffsetBox`.
    
    This function creates a grid of subplots with diagonal lines and surrounding offset boxes. It demonstrates how `tight_layout` handles these boxes and ensures they are properly positioned without overlapping.
    
    Parameters:
    None
    
    Returns:
    None
    
    Steps:
    1. Creates a 2x2 grid of subplots.
    2. Plots a diagonal line on each subplot.
    3. Adds 7 offset
    """

    # 1.
    # - Create 4 subplots
    # - Plot a diagonal line on them
    # - Surround each plot with 7 boxes
    # - Use tight_layout
    # - See that the squares are included in the tight_layout
    #   and that the squares in the middle do not overlap
    #
    # 2.
    # - Make the squares around the right side axes invisible
    # - See that the invisible squares do not affect the
    #   tight_layout
    rows = cols = 2
    colors = ['red', 'blue', 'green', 'yellow']
    x = y = [0, 1]

    def _subplots():
        """
        Generates subplots with specified rows and columns.
        
        This function creates a grid of subplots based on the given number of rows and columns. It then iterates over each subplot, plotting a line graph using the provided x and y data points, and applying an offsetbox customization with a specified offset value. The function returns the array of axes objects.
        
        Parameters:
        None
        
        Returns:
        axs (numpy.ndarray): An array of matplotlib Axes objects representing the subplots.
        
        Usage:
        """

        _, axs = plt.subplots(rows, cols)
        axs = axs.flat
        for ax, color in zip(axs, colors):
            ax.plot(x, y, color=color)
            add_offsetboxes(ax, 20, color=color)
        return axs

    # 1.
    axs = _subplots()
    plt.tight_layout()

    # 2.
    axs = _subplots()
    for ax in (axs[cols-1::rows]):
        for child in ax.get_children():
            if isinstance(child, AnchoredOffsetbox):
                child.set_visible(False)

    plt.tight_layout()


def test_empty_layout():
    """Test that tight layout doesn't cause an error when there are no axes."""
    fig = plt.gcf()
    fig.tight_layout()


@pytest.mark.parametrize("label", ["xlabel", "ylabel"])
def test_verybig_decorators(label):
    """Test that no warning emitted when xlabel/ylabel too big."""
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.set(**{label: 'a' * 100})


def test_big_decorators_horizontal():
    """Test that doesn't warn when xlabel too big."""
    fig, axs = plt.subplots(1, 2, figsize=(3, 2))
    axs[0].set_xlabel('a' * 30)
    axs[1].set_xlabel('b' * 30)


def test_big_decorators_vertical():
    """Test that doesn't warn when ylabel too big."""
    fig, axs = plt.subplots(2, 1, figsize=(3, 2))
    axs[0].set_ylabel('a' * 20)
    axs[1].set_ylabel('b' * 20)


def test_badsubplotgrid():
    """
    Test for handling mismatched subplot grids.
    
    This function checks if a warning is raised when using `plt.subplot2grid`
    with mismatched grid dimensions. It creates two subplots with different
    grid specifications and uses `plt.tight_layout` to adjust the spacing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    UserWarning: If the mismatched subplot grids do not trigger a warning.
    
    Functions Used:
    - `plt.subplot2grid`: Creates a
    """

    # test that we get warning for mismatched subplot grids, not than an error
    plt.subplot2grid((4, 5), (0, 0))
    # this is the bad entry:
    plt.subplot2grid((5, 5), (0, 3), colspan=3, rowspan=5)
    with pytest.warns(UserWarning):
        plt.tight_layout()


def test_collapsed():
    """
    Test that `tight_layout` does not collapse axes when annotations cause
    layout to exceed figure boundaries.
    
    This function creates a figure with a single axis, sets its limits, and
    adds an annotation with a long string. It then checks whether the axis's
    position remains unchanged after calling `tight_layout`. The test also
    verifies that `tight_layout` does not crash when a specific rectangle is
    passed as an argument.
    
    Parameters:
    None
    
    Returns:
    """

    # test that if the amount of space required to make all the axes
    # decorations fit would mean that the actual Axes would end up with size
    # zero (i.e. margins add up to more than the available width) that a call
    # to tight_layout will not get applied:
    fig, ax = plt.subplots(tight_layout=True)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    ax.annotate('BIG LONG STRING', xy=(1.25, 2), xytext=(10.5, 1.75),
                annotation_clip=False)
    p1 = ax.get_position()
    with pytest.warns(UserWarning):
        plt.tight_layout()
        p2 = ax.get_position()
        assert p1.width == p2.width
    # test that passing a rect doesn't crash...
    with pytest.warns(UserWarning):
        plt.tight_layout(rect=[0, 0, 0.8, 0.8])


def test_suptitle():
    """
    Test the vertical positioning of the suptitle relative to the title of an axis.
    
    This function creates a figure with a single subplot and sets the suptitle
    and title of the subplot. It then checks if the y-coordinate of the bottom
    edge of the suptitle is greater than the y-coordinate of the top edge of
    the subplot title.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots()`: Creates
    """

    fig, ax = plt.subplots(tight_layout=True)
    st = fig.suptitle("foo")
    t = ax.set_title("bar")
    fig.canvas.draw()
    assert st.get_window_extent().y0 > t.get_window_extent().y1


@pytest.mark.backend("pdf")
def test_non_agg_renderer(monkeypatch, recwarn):
    """
    Test non-agg renderer.
    
    This function checks that the RendererBase initialization does not instantiate any other renderer than a PDF renderer to perform PDF tight layout. It sets up a figure and axes object using `plt.subplots()` and then applies `fig.tight_layout()` to ensure proper layout adjustments.
    
    Parameters:
    -----------
    monkeypatch : fixture
    A pytest fixture used to temporarily replace or inject objects into the system under test.
    recwarn : fixture
    A pytest fixture used to capture
    """

    unpatched_init = mpl.backend_bases.RendererBase.__init__

    def __init__(self, *args, **kwargs):
        """
        Initializes an instance of the class with the given arguments and keyword arguments. Ensures that the instance is an instance of `mpl.backends.backend_pdf.RendererPdf` to enable PDF tight layout. Calls the `unpatched_init` function with the provided arguments and keyword arguments.
        """

        # Check that we don't instantiate any other renderer than a pdf
        # renderer to perform pdf tight layout.
        assert isinstance(self, mpl.backends.backend_pdf.RendererPdf)
        unpatched_init(self, *args, **kwargs)

    monkeypatch.setattr(mpl.backend_bases.RendererBase, "__init__", __init__)
    fig, ax = plt.subplots()
    fig.tight_layout()


def test_manual_colorbar():
    """
    Generate a Python docstring for the provided function.
    
    Args:
    None
    
    Returns:
    None
    
    Summary:
    This function creates a figure with two subplots and adds a scatter plot to the second subplot. It then creates a colorbar for the scatter plot and adds it to the figure. Finally, it attempts to apply tight layout to the figure, which may generate a warning due to the presence of multiple Axes objects.
    """

    # This should warn, but not raise
    fig, axes = plt.subplots(1, 2)
    pts = axes[1].scatter([0, 1], [0, 1], c=[1, 5])
    ax_rect = axes[1].get_position()
    cax = fig.add_axes(
        [ax_rect.x1 + 0.005, ax_rect.y0, 0.015, ax_rect.height]
    )
    fig.colorbar(pts, cax=cax)
    with pytest.warns(UserWarning, match="This figure includes Axes"):
        fig.tight_layout()


def test_clipped_to_axes():
    """
    Test whether artists are fully clipped to the axes.
    
    This function checks if artists are fully clipped to the axes under
    different conditions. It iterates over subplots with various projections,
    plots arrays using `plot` and `pcolor`, and verifies if the resulting
    handles (`h`) and mappable objects (`m`) are fully clipped to the axes.
    The function also demonstrates how setting custom clip paths can affect
    the clipping status of these artists.
    
    Parameters:
    """

    # Ensure that _fully_clipped_to_axes() returns True under default
    # conditions for all projection types. Axes.get_tightbbox()
    # uses this to skip artists in layout calculations.
    arr = np.arange(100).reshape((10, 10))
    fig = plt.figure(figsize=(6, 2))
    ax1 = fig.add_subplot(131, projection='rectilinear')
    ax2 = fig.add_subplot(132, projection='mollweide')
    ax3 = fig.add_subplot(133, projection='polar')
    for ax in (ax1, ax2, ax3):
        # Default conditions (clipped by ax.bbox or ax.patch)
        ax.grid(False)
        h, = ax.plot(arr[:, 0])
        m = ax.pcolor(arr)
        assert h._fully_clipped_to_axes()
        assert m._fully_clipped_to_axes()
        # Non-default conditions (not clipped by ax.patch)
        rect = Rectangle((0, 0), 0.5, 0.5, transform=ax.transAxes)
        h.set_clip_path(rect)
        m.set_clip_path(rect.get_path(), rect.get_transform())
        assert not h._fully_clipped_to_axes()
        assert not m._fully_clipped_to_axes()


def test_tight_pads():
    """
    Set tight layout parameters for the figure.
    
    This function creates a new figure and sets its tight layout parameters
    using the `set_tight_layout` method. It also generates a warning using
    `pytest.warns` indicating that the method will be deprecated in future.
    The function then draws the figure without rendering it using
    `fig.draw_without_rendering`.
    
    Parameters:
    None
    
    Returns:
    None
    """

    fig, ax = plt.subplots()
    with pytest.warns(PendingDeprecationWarning,
                      match='will be deprecated'):
        fig.set_tight_layout({'pad': 0.15})
    fig.draw_without_rendering()


def test_tight_kwargs():
    fig, ax = plt.subplots(tight_layout={'pad': 0.15})
    fig.draw_without_rendering()
