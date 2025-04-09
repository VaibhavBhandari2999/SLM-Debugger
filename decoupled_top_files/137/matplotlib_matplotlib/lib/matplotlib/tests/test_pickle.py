from io import BytesIO
import ast
import pickle

import numpy as np
import pytest

import matplotlib as mpl
from matplotlib import cm
from matplotlib.testing import subprocess_run_helper
from matplotlib.testing.decorators import check_figures_equal
from matplotlib.dates import rrulewrapper
from matplotlib.lines import VertexSelector
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.figure as mfigure
from mpl_toolkits.axes_grid1 import parasite_axes


def test_simple():
    """
    Pickles various matplotlib figures and axes objects.
    
    This function creates multiple matplotlib figures and axes, applies different plotting commands, and pickles them into a BytesIO object. The key operations include creating a figure with subplots, adding polar and bar plots, setting log scale, and using different projections.
    
    Args:
    None
    
    Returns:
    None
    """

    fig = plt.figure()
    pickle.dump(fig, BytesIO(), pickle.HIGHEST_PROTOCOL)

    ax = plt.subplot(121)
    pickle.dump(ax, BytesIO(), pickle.HIGHEST_PROTOCOL)

    ax = plt.axes(projection='polar')
    plt.plot(np.arange(10), label='foobar')
    plt.legend()

    pickle.dump(ax, BytesIO(), pickle.HIGHEST_PROTOCOL)

#    ax = plt.subplot(121, projection='hammer')
#    pickle.dump(ax, BytesIO(), pickle.HIGHEST_PROTOCOL)

    plt.figure()
    plt.bar(x=np.arange(10), height=np.arange(10))
    pickle.dump(plt.gca(), BytesIO(), pickle.HIGHEST_PROTOCOL)

    fig = plt.figure()
    ax = plt.axes()
    plt.plot(np.arange(10))
    ax.set_yscale('log')
    pickle.dump(fig, BytesIO(), pickle.HIGHEST_PROTOCOL)


def _generate_complete_test_figure(fig_ref):
    """
    Generates a complete test figure with various plots.
    
    This function creates a figure with a suptitle and multiple subplots containing different types of plots such as line plot, contour plot, pcolor plot, image plot, stream plot, quiver plot, scatter plot, and error bar plot. The figure size is set to (10, 6) inches.
    
    Parameters:
    fig_ref (matplotlib.figure.Figure): A reference to the matplotlib figure object.
    
    Returns:
    None
    """

    fig_ref.set_size_inches((10, 6))
    plt.figure(fig_ref)

    plt.suptitle('Can you fit any more in a figure?')

    # make some arbitrary data
    x, y = np.arange(8), np.arange(10)
    data = u = v = np.linspace(0, 10, 80).reshape(10, 8)
    v = np.sin(v * -0.6)

    # Ensure lists also pickle correctly.
    plt.subplot(3, 3, 1)
    plt.plot(list(range(10)))

    plt.subplot(3, 3, 2)
    plt.contourf(data, hatches=['//', 'ooo'])
    plt.colorbar()

    plt.subplot(3, 3, 3)
    plt.pcolormesh(data)

    plt.subplot(3, 3, 4)
    plt.imshow(data)

    plt.subplot(3, 3, 5)
    plt.pcolor(data)

    ax = plt.subplot(3, 3, 6)
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 9)
    plt.streamplot(x, y, u, v)

    ax = plt.subplot(3, 3, 7)
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 9)
    plt.quiver(x, y, u, v)

    plt.subplot(3, 3, 8)
    plt.scatter(x, x ** 2, label='$x^2$')
    plt.legend(loc='upper left')

    plt.subplot(3, 3, 9)
    plt.errorbar(x, x * -0.5, xerr=0.2, yerr=0.4)


@mpl.style.context("default")
@check_figures_equal(extensions=["png"])
def test_complete(fig_test, fig_ref):
    """
    Test the completeness of a figure by comparing it with a reference figure.
    
    This function generates a complete test figure using `_generate_complete_test_figure`, then compares it with a reference figure by pickling and unpickling the reference figure. The test figure's size is adjusted to match the reference figure, and the reference figure's content is overlaid on the test figure. Finally, the reference figure is closed.
    
    Parameters:
    fig_test (matplotlib.figure.Figure): The test figure to be compared
    """

    _generate_complete_test_figure(fig_ref)
    # plotting is done, now test its pickle-ability
    pkl = BytesIO()
    pickle.dump(fig_ref, pkl, pickle.HIGHEST_PROTOCOL)
    loaded = pickle.loads(pkl.getbuffer())
    loaded.canvas.draw()

    fig_test.set_size_inches(loaded.get_size_inches())
    fig_test.figimage(loaded.canvas.renderer.buffer_rgba())

    plt.close(loaded)


def _pickle_load_subprocess():
    """
    Load a pickled figure from a file in a subprocess.
    
    This function reads a pickled figure from a specified file path using the `pickle` module and prints the serialized representation of the figure.
    
    Args:
    None
    
    Returns:
    None
    
    Environment Variables:
    PICKLE_FILE_PATH (str): The file path to the pickled figure.
    
    Functions Used:
    - `os.environ`: Accesses the environment variable `PICKLE_FILE_PATH`.
    - `open`:
    """

    import os
    import pickle

    path = os.environ['PICKLE_FILE_PATH']

    with open(path, 'rb') as blob:
        fig = pickle.load(blob)

    print(str(pickle.dumps(fig)))


@mpl.style.context("default")
@check_figures_equal(extensions=['png'])
def test_pickle_load_from_subprocess(fig_test, fig_ref, tmp_path):
    """
    Load a figure from a pickled file in a subprocess and compare it with the original figure.
    
    This function generates a reference figure, pickles it, and then loads it in a subprocess. The loaded figure is compared with the original figure by adjusting their sizes and overlaying one on top of the other.
    
    Parameters:
    fig_test (matplotlib.figure.Figure): The figure to be tested.
    fig_ref (matplotlib.figure.Figure): The reference figure to be pickled and loaded.
    """

    _generate_complete_test_figure(fig_ref)

    fp = tmp_path / 'sinus.pickle'
    assert not fp.exists()

    with fp.open('wb') as file:
        pickle.dump(fig_ref, file, pickle.HIGHEST_PROTOCOL)
    assert fp.exists()

    proc = subprocess_run_helper(
        _pickle_load_subprocess,
        timeout=60,
        extra_env={'PICKLE_FILE_PATH': str(fp)}
    )

    loaded_fig = pickle.loads(ast.literal_eval(proc.stdout))

    loaded_fig.canvas.draw()

    fig_test.set_size_inches(loaded_fig.get_size_inches())
    fig_test.figimage(loaded_fig.canvas.renderer.buffer_rgba())

    plt.close(loaded_fig)


def test_gcf():
    """
    Test the functionality of creating and managing figures using Matplotlib.
    
    This function creates a figure with a specified label, pickles it, closes all figures,
    and then unpickles the figure to verify that the figure management system still retains
    the figure and its label.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    - Matplotlib
    - Figure
    - Pickle
    - Gcf.figs
    - plt._pylab_helpers
    """

    fig = plt.figure("a label")
    buf = BytesIO()
    pickle.dump(fig, buf, pickle.HIGHEST_PROTOCOL)
    plt.close("all")
    assert plt._pylab_helpers.Gcf.figs == {}  # No figures must be left.
    fig = pickle.loads(buf.getbuffer())
    assert plt._pylab_helpers.Gcf.figs != {}  # A manager is there again.
    assert fig.get_label() == "a label"


def test_no_pyplot():
    """
    Tests the pickle-ability of a figure that is not created using `pyplot`.
    
    This function creates a figure using `matplotlib.figure.Figure` and a
    `FigureCanvasPdf` object. It then adds an axis to the figure and plots a
    simple line graph. The figure is pickled using `pickle.dump` and stored in
    a `BytesIO` object.
    
    Args:
    None
    
    Returns:
    None
    """

    # tests pickle-ability of a figure not created with pyplot
    from matplotlib.backends.backend_pdf import FigureCanvasPdf
    fig = mfigure.Figure()
    _ = FigureCanvasPdf(fig)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3], [1, 2, 3])
    pickle.dump(fig, BytesIO(), pickle.HIGHEST_PROTOCOL)


def test_renderer():
    """
    Generate a Matplotlib renderer object and serialize it.
    
    This function creates an instance of `RendererAgg` with specified dimensions and DPI, then serializes the object using `pickle.dump()` into a `BytesIO` buffer.
    
    Parameters:
    None
    
    Returns:
    None
    """

    from matplotlib.backends.backend_agg import RendererAgg
    renderer = RendererAgg(10, 20, 30)
    pickle.dump(renderer, BytesIO())


def test_image():
    """
    Save a Matplotlib figure with an image to a pickle object.
    
    This function creates a new figure, adds an image to it using `imshow`,
    draws the figure, and then pickles the figure object to a BytesIO buffer.
    
    Parameters:
    None
    
    Returns:
    bytes: A pickled representation of the Matplotlib figure containing the image.
    """

    # Prior to v1.4.0 the Image would cache data which was not picklable
    # once it had been drawn.
    from matplotlib.backends.backend_agg import new_figure_manager
    manager = new_figure_manager(1000)
    fig = manager.canvas.figure
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(np.arange(12).reshape(3, 4))
    manager.canvas.draw()
    pickle.dump(fig, BytesIO())


def test_polar():
    """
    Generate a polar plot using Matplotlib, serialize the figure object using pickle, and deserialize it back to verify its integrity.
    
    Args:
    None
    
    Returns:
    None
    
    Summary:
    This function creates a polar plot using Matplotlib's subplot function with polar=True. It then serializes the current figure object (fig) into a pickled format using pickle.dumps(). The pickled figure is deserialized using pickle.loads() to ensure its integrity. Finally, the figure is drawn using plt
    """

    plt.subplot(polar=True)
    fig = plt.gcf()
    pf = pickle.dumps(fig)
    pickle.loads(pf)
    plt.draw()


class TransformBlob:
    def __init__(self):
        """
        Initializes an object with two identity transforms, a composite transform, and two transform wrappers.
        
        This method sets up the initial state of the object by creating two `IdentityTransform` instances, `identity` and `identity2`. It then creates a `CompositeGenericTransform` instance named `composite`, using `identity` and `identity2` as its components. The `TransformWrapper` is applied to `composite`, resulting in `wrapper`. Another `CompositeGenericTransform` instance, `composite2
        """

        self.identity = mtransforms.IdentityTransform()
        self.identity2 = mtransforms.IdentityTransform()
        # Force use of the more complex composition.
        self.composite = mtransforms.CompositeGenericTransform(
            self.identity,
            self.identity2)
        # Check parent -> child links of TransformWrapper.
        self.wrapper = mtransforms.TransformWrapper(self.composite)
        # Check child -> parent links of TransformWrapper.
        self.composite2 = mtransforms.CompositeGenericTransform(
            self.wrapper,
            self.identity)


def test_transform():
    """
    Test the transformation process involving a TransformBlob object, including serialization, deserialization, and verification of the integrity of the object's structure and dimensions through the use of pickle, TransformWrapper, and composite objects.
    """

    obj = TransformBlob()
    pf = pickle.dumps(obj)
    del obj

    obj = pickle.loads(pf)
    # Check parent -> child links of TransformWrapper.
    assert obj.wrapper._child == obj.composite
    # Check child -> parent links of TransformWrapper.
    assert [v() for v in obj.wrapper._parents.values()] == [obj.composite2]
    # Check input and output dimensions are set as expected.
    assert obj.wrapper.input_dims == obj.composite.input_dims
    assert obj.wrapper.output_dims == obj.composite.output_dims


def test_rrulewrapper():
    """
    Test the pickling functionality of the rrulewrapper object.
    
    This function tests whether an instance of rrulewrapper with a frequency of 2 can be successfully pickled and unpickled without raising a RecursionError.
    
    Args:
    None
    
    Returns:
    None
    """

    r = rrulewrapper(2)
    try:
        pickle.loads(pickle.dumps(r))
    except RecursionError:
        print('rrulewrapper pickling test failed')
        raise


def test_shared():
    """
    Set shared x-axis limits across subplots.
    
    This function creates a figure with two subplots sharing the same x-axis,
    sets the x-axis limits of the first subplot, and ensures that the second
    subplot has the same x-axis limits.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> test_shared()
    # The function will create a figure with two subplots and set their x-axis limits to (10, 20).
    """

    fig, axs = plt.subplots(2, sharex=True)
    fig = pickle.loads(pickle.dumps(fig))
    fig.axes[0].set_xlim(10, 20)
    assert fig.axes[1].get_xlim() == (10, 20)


def test_inset_and_secondary():
    """
    Create a figure with an inset axes and secondary x-axis.
    
    This function generates a matplotlib figure with an inset axes and a
    secondary x-axis that applies a square and square root transformation.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The created figure object.
    ax (matplotlib.axes.Axes): The main axes of the figure.
    """

    fig, ax = plt.subplots()
    ax.inset_axes([.1, .1, .3, .3])
    ax.secondary_xaxis("top", functions=(np.square, np.sqrt))
    pickle.loads(pickle.dumps(fig))


@pytest.mark.parametrize("cmap", cm._colormaps.values())
def test_cmap(cmap):
    pickle.dumps(cmap)


def test_unpickle_canvas():
    """
    Unpickles a matplotlib figure and checks if the canvas attribute is preserved.
    
    This function creates a matplotlib figure, pickles it, unpickles it, and verifies that the canvas attribute remains intact.
    
    Args:
    None
    
    Returns:
    None
    
    Functions Used:
    - `mfigure.Figure()`: Creates a new matplotlib figure.
    - `BytesIO()`: A binary buffer in memory.
    - `pickle.dump()`: Serializes the figure object into a byte
    """

    fig = mfigure.Figure()
    assert fig.canvas is not None
    out = BytesIO()
    pickle.dump(fig, out)
    out.seek(0)
    fig2 = pickle.load(out)
    assert fig2.canvas is not None


def test_mpl_toolkits():
    ax = parasite_axes.host_axes([0, 0, 1, 1])
    assert type(pickle.loads(pickle.dumps(ax))) == parasite_axes.HostAxes


def test_standard_norm():
    assert type(pickle.loads(pickle.dumps(mpl.colors.LogNorm()))) \
        == mpl.colors.LogNorm


def test_dynamic_norm():
    """
    Test the dynamic norm functionality using `mpl.colors.make_norm_from_scale` with `LogitScale` and `Normalize`. This function creates an instance of the dynamic norm and ensures that its pickled and unpickled version retains the same type.
    
    Args:
    None
    
    Returns:
    None
    """

    logit_norm_instance = mpl.colors.make_norm_from_scale(
        mpl.scale.LogitScale, mpl.colors.Normalize)()
    assert type(pickle.loads(pickle.dumps(logit_norm_instance))) \
        == type(logit_norm_instance)


def test_vertexselector():
    line, = plt.plot([0, 1], picker=True)
    pickle.loads(pickle.dumps(VertexSelector(line)))
