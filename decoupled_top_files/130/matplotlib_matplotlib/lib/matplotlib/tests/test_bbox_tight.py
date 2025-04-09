from io import BytesIO

import numpy as np

from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter


@image_comparison(['bbox_inches_tight'], remove_text=True,
                  savefig_kwarg={'bbox_inches': 'tight'})
def test_bbox_inches_tight():
    """
    Test that a figure saved using bbox_inches='tight' is clipped correctly.
    
    This function creates a stacked bar chart with a table at the bottom. The
    chart uses the `plt.bar` function to create the bars and the `plt.table`
    function to add the table. The figure is saved with `bbox_inches='tight'`
    to ensure proper clipping of the table and legend.
    """

    #: Test that a figure saved using bbox_inches='tight' is clipped correctly
    data = [[66386, 174296, 75131, 577908, 32015],
            [58230, 381139, 78045, 99308, 160454],
            [89135, 80552, 152558, 497981, 603535],
            [78415, 81858, 150656, 193263, 69638],
            [139361, 331509, 343164, 781380, 52269]]

    col_labels = row_labels = [''] * 5

    rows = len(data)
    ind = np.arange(len(col_labels)) + 0.3  # the x locations for the groups
    cell_text = []
    width = 0.4  # the width of the bars
    yoff = np.zeros(len(col_labels))
    # the bottom values for stacked bar chart
    fig, ax = plt.subplots(1, 1)
    for row in range(rows):
        ax.bar(ind, data[row], width, bottom=yoff, align='edge', color='b')
        yoff = yoff + data[row]
        cell_text.append([''])
    plt.xticks([])
    plt.xlim(0, 5)
    plt.legend([''] * 5, loc=(1.2, 0.2))
    fig.legend([''] * 5, bbox_to_anchor=(0, 0.2), loc='lower left')
    # Add a table at the bottom of the axes
    cell_text.reverse()
    plt.table(cellText=cell_text, rowLabels=row_labels, colLabels=col_labels,
              loc='bottom')


@image_comparison(['bbox_inches_tight_suptile_legend'],
                  savefig_kwarg={'bbox_inches': 'tight'})
def test_bbox_inches_tight_suptile_legend():
    """
    Generate a plot with a tight bounding box, legend, and suptitle.
    
    This function creates a plot of a straight line with a legend placed at (0.9, 1) in the upper left corner. The plot includes a title, a figure title, and a custom y-axis tick formatter. The bounding box is adjusted to account for the legend and the long y tick label.
    
    Parameters:
    None
    
    Returns:
    None
    """

    plt.plot(np.arange(10), label='a straight line')
    plt.legend(bbox_to_anchor=(0.9, 1), loc='upper left')
    plt.title('Axis title')
    plt.suptitle('Figure title')

    # put an extra long y tick on to see that the bbox is accounted for
    def y_formatter(y, pos):
        """
        Format y-axis labels.
        
        This function takes a value `y` and its corresponding position `pos` on the y-axis and returns a formatted string based on the value of `y`. If `y` is equal to 4, it returns the string 'The number 4'. Otherwise, it returns the string representation of `y`.
        
        Parameters:
        -----------
        y : float
        The value of the y-coordinate.
        pos : int
        The position of the y-coordinate
        """

        if int(y) == 4:
            return 'The number 4'
        else:
            return str(y)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))

    plt.xlabel('X axis')


@image_comparison(['bbox_inches_tight_suptile_non_default.png'],
                  savefig_kwarg={'bbox_inches': 'tight'},
                  tol=0.1)  # large tolerance because only testing clipping.
def test_bbox_inches_tight_suptitle_non_default():
    fig, ax = plt.subplots()
    fig.suptitle('Booo', x=0.5, y=1.1)


@image_comparison(['bbox_inches_tight_clipping'],
                  remove_text=True, savefig_kwarg={'bbox_inches': 'tight'})
def test_bbox_inches_tight_clipping():
    """
    Tests bounding box (bbox) clipping for scatter plots and path clipping for patches.
    
    This function creates a scatter plot of 10 points and sets the x and y limits to [0, 5]. It then creates a blue rectangular patch with dimensions 100x100, centered at (-50, -50), and clips this patch using a star-shaped path defined by `mpath.Path.unit_regular_star(5)` scaled down by a factor of 0.
    """

    # tests bbox clipping on scatter points, and path clipping on a patch
    # to generate an appropriately tight bbox
    plt.scatter(np.arange(10), np.arange(10))
    ax = plt.gca()
    ax.set_xlim([0, 5])
    ax.set_ylim([0, 5])

    # make a massive rectangle and clip it with a path
    patch = mpatches.Rectangle([-50, -50], 100, 100,
                               transform=ax.transData,
                               facecolor='blue', alpha=0.5)

    path = mpath.Path.unit_regular_star(5).deepcopy()
    path.vertices *= 0.25
    patch.set_clip_path(path, transform=ax.transAxes)
    plt.gcf().artists.append(patch)


@image_comparison(['bbox_inches_tight_raster'],
                  remove_text=True, savefig_kwarg={'bbox_inches': 'tight'})
def test_bbox_inches_tight_raster():
    """Test rasterization with tight_layout"""
    fig, ax = plt.subplots()
    ax.plot([1.0, 2.0], rasterized=True)


def test_only_on_non_finite_bbox():
    """
    Test saving a figure with a non-finite bounding box.
    
    This function creates a figure with an axis that has a non-finite bounding
    box (specifically, a `NaN` value). It then attempts to save the figure using
    `fig.savefig()` with `bbox_inches='tight'` and format set to 'png'. The
    primary goal is to ensure that the function does not raise any errors during
    the saving process.
    
    Parameters:
    None
    """

    fig, ax = plt.subplots()
    ax.annotate("", xy=(0, float('nan')))
    ax.set_axis_off()
    # we only need to test that it does not error out on save
    fig.savefig(BytesIO(), bbox_inches='tight', format='png')


def test_tight_pcolorfast():
    """
    Test pcolorfast with tight bounding box.
    
    This function creates a figure with an axes containing a pcolorfast plot
    and sets the y-axis limits to (0, 0.1). The figure is saved to a buffer
    with a tight bounding box, and the dimensions of the resulting image are
    checked to ensure that the width is greater than the height. This tests
    whether the bounding box correctly excludes the clipped area of the image
    due to the y
    """

    fig, ax = plt.subplots()
    ax.pcolorfast(np.arange(4).reshape((2, 2)))
    ax.set(ylim=(0, .1))
    buf = BytesIO()
    fig.savefig(buf, bbox_inches="tight")
    buf.seek(0)
    height, width, _ = plt.imread(buf).shape
    # Previously, the bbox would include the area of the image clipped out by
    # the axes, resulting in a very tall image given the y limits of (0, 0.1).
    assert width > height


def test_noop_tight_bbox():
    """
    Test that saving a figure with a tight bounding box and no padding does not alter the image when using a rasterized artist.
    
    This function creates a figure with a specific size and DPI, adds an axes without visible axis, and displays an image using `imshow`. The figure is saved twice: once with a tight bounding box and no padding, and once again with the same settings. The resulting images are compared to ensure that the second save operation does not modify the image data, particularly focusing on the
    """

    from PIL import Image
    x_size, y_size = (10, 7)
    dpi = 100
    # make the figure just the right size up front
    fig = plt.figure(frameon=False, dpi=dpi, figsize=(x_size/dpi, y_size/dpi))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.set_axis_off()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    data = np.arange(x_size * y_size).reshape(y_size, x_size)
    ax.imshow(data, rasterized=True)

    # When a rasterized Artist is included, a mixed-mode renderer does
    # additional bbox adjustment. It should also be a no-op, and not affect the
    # next save.
    fig.savefig(BytesIO(), bbox_inches='tight', pad_inches=0, format='pdf')

    out = BytesIO()
    fig.savefig(out, bbox_inches='tight', pad_inches=0)
    out.seek(0)
    im = np.asarray(Image.open(out))
    assert (im[:, :, 3] == 255).all()
    assert not (im[:, :, :3] == 255).all()
    assert im.shape == (7, 10, 4)
