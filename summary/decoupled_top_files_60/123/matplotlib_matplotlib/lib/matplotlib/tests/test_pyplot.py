import difflib
import re

import numpy as np
import subprocess
import sys
from pathlib import Path

import pytest

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib._api import MatplotlibDeprecationWarning


def test_pyplot_up_to_date(tmpdir):
    """
    Ensures that the `pyplot.py` file is up-to-date with the latest changes from the `boilerplate.py` script.
    
    This function checks if the `boilerplate.py` script exists, and if not, skips the test. It then reads the original content of `pyplot.py` and writes it to a temporary file. The `boilerplate.py` script is run on this temporary file to update its content. If the updated content differs from the original, a detailed
    """

    gen_script = Path(mpl.__file__).parents[2] / "tools/boilerplate.py"
    if not gen_script.exists():
        pytest.skip("boilerplate.py not found")
    orig_contents = Path(plt.__file__).read_text()
    plt_file = tmpdir.join('pyplot.py')
    plt_file.write_text(orig_contents, 'utf-8')

    subprocess.run([sys.executable, str(gen_script), str(plt_file)],
                   check=True)
    new_contents = plt_file.read_text('utf-8')

    if orig_contents != new_contents:
        diff_msg = '\n'.join(
            difflib.unified_diff(
                orig_contents.split('\n'), new_contents.split('\n'),
                fromfile='found pyplot.py',
                tofile='expected pyplot.py',
                n=0, lineterm=''))
        pytest.fail(
            "pyplot.py is not up-to-date. Please run "
            "'python tools/boilerplate.py' to update pyplot.py. "
            "This needs to be done from an environment where your "
            "current working copy is installed (e.g. 'pip install -e'd). "
            "Here is a diff of unexpected differences:\n%s" % diff_msg
        )


def test_copy_docstring_and_deprecators(recwarn):
    @mpl._api.rename_parameter("(version)", "old", "new")
    @mpl._api.make_keyword_only("(version)", "kwo")
    def func(new, kwo=None):
        pass

    @plt._copy_docstring_and_deprecators(func)
    def wrapper_func(new, kwo=None):
        pass

    wrapper_func(None)
    wrapper_func(new=None)
    wrapper_func(None, kwo=None)
    wrapper_func(new=None, kwo=None)
    assert not recwarn
    with pytest.warns(MatplotlibDeprecationWarning):
        wrapper_func(old=None)
    with pytest.warns(MatplotlibDeprecationWarning):
        wrapper_func(None, None)


def test_pyplot_box():
    fig, ax = plt.subplots()
    plt.box(False)
    assert not ax.get_frame_on()
    plt.box(True)
    assert ax.get_frame_on()
    plt.box()
    assert not ax.get_frame_on()
    plt.box()
    assert ax.get_frame_on()


def test_stackplot_smoke():
    # Small smoke test for stackplot (see #12405)
    plt.stackplot([1, 2, 3], [1, 2, 3])


def test_nrows_error():
    """
    Function: test_nrows_error
    
    This function is designed to test for type errors in the `plt.subplot` function when using the `nrows` and `ncols` parameters.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    - TypeError: If `plt.subplot` is called with `nrows` or `ncols` parameters, as these parameters are not valid for the function.
    
    Usage:
    This function is used to ensure that the `plt.subplot` function raises a TypeError when it
    """

    with pytest.raises(TypeError):
        plt.subplot(nrows=1)
    with pytest.raises(TypeError):
        plt.subplot(ncols=1)


def test_ioff():
    plt.ion()
    assert mpl.is_interactive()
    with plt.ioff():
        assert not mpl.is_interactive()
    assert mpl.is_interactive()

    plt.ioff()
    assert not mpl.is_interactive()
    with plt.ioff():
        assert not mpl.is_interactive()
    assert not mpl.is_interactive()


def test_ion():
    plt.ioff()
    assert not mpl.is_interactive()
    with plt.ion():
        assert mpl.is_interactive()
    assert not mpl.is_interactive()

    plt.ion()
    assert mpl.is_interactive()
    with plt.ion():
        assert mpl.is_interactive()
    assert mpl.is_interactive()


def test_nested_ion_ioff():
    """
    Test the interaction between 'ion' and 'ioff' context managers for controlling interactive mode in Matplotlib.
    
    This function checks the behavior of the 'ion' and 'ioff' context managers, which control whether Matplotlib figures are displayed interactively or not. The function tests various combinations of these context managers to ensure they work as expected.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Input:
    - None
    
    Output:
    - None
    
    Behavior:
    - The function tests the interaction between
    """

    # initial state is interactive
    plt.ion()

    # mixed ioff/ion
    with plt.ioff():
        assert not mpl.is_interactive()
        with plt.ion():
            assert mpl.is_interactive()
        assert not mpl.is_interactive()
    assert mpl.is_interactive()

    # redundant contexts
    with plt.ioff():
        with plt.ioff():
            assert not mpl.is_interactive()
    assert mpl.is_interactive()

    with plt.ion():
        plt.ioff()
    assert mpl.is_interactive()

    # initial state is not interactive
    plt.ioff()

    # mixed ioff/ion
    with plt.ion():
        assert mpl.is_interactive()
        with plt.ioff():
            assert not mpl.is_interactive()
        assert mpl.is_interactive()
    assert not mpl.is_interactive()

    # redundant contexts
    with plt.ion():
        with plt.ion():
            assert mpl.is_interactive()
    assert not mpl.is_interactive()

    with plt.ioff():
        plt.ion()
    assert not mpl.is_interactive()


def test_close():
    try:
        plt.close(1.1)
    except TypeError as e:
        assert str(e) == "close() argument must be a Figure, an int, " \
                         "a string, or None, not <class 'float'>"


def test_subplot_reuse():
    """
    Create and reuse subplots in a figure.
    
    This function demonstrates the creation and reuse of subplots within a single figure using matplotlib's `plt.subplot` method.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key behavior:
    1. Creates the first subplot and asserts that the returned axes object is the current axes.
    2. Creates the second subplot and asserts that the returned axes object is the current axes.
    3. Re-creates the first subplot and asserts that the same axes object is returned and is the current
    """

    ax1 = plt.subplot(121)
    assert ax1 is plt.gca()
    ax2 = plt.subplot(122)
    assert ax2 is plt.gca()
    ax3 = plt.subplot(121)
    assert ax1 is plt.gca()
    assert ax1 is ax3


def test_axes_kwargs():
    # plt.axes() always creates new axes, even if axes kwargs differ.
    plt.figure()
    ax = plt.axes()
    ax1 = plt.axes()
    assert ax is not None
    assert ax1 is not ax
    plt.close()

    plt.figure()
    ax = plt.axes(projection='polar')
    ax1 = plt.axes(projection='polar')
    assert ax is not None
    assert ax1 is not ax
    plt.close()

    plt.figure()
    ax = plt.axes(projection='polar')
    ax1 = plt.axes()
    assert ax is not None
    assert ax1.name == 'rectilinear'
    assert ax1 is not ax
    plt.close()


def test_subplot_replace_projection():
    # plt.subplot() searches for axes with the same subplot spec, and if one
    # exists, and the kwargs match returns it, create a new one if they do not
    fig = plt.figure()
    ax = plt.subplot(1, 2, 1)
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    with pytest.warns(MatplotlibDeprecationWarning):
        ax3 = plt.subplot(1, 2, 1, projection='polar')
    ax4 = plt.subplot(1, 2, 1, projection='polar')
    assert ax is not None
    assert ax1 is ax
    assert ax2 is not ax
    assert ax3 is not ax
    assert ax3 is ax4

    assert ax not in fig.axes
    assert ax2 in fig.axes
    assert ax3 in fig.axes

    assert ax.name == 'rectilinear'
    assert ax2.name == 'rectilinear'
    assert ax3.name == 'polar'


def test_subplot_kwarg_collision():
    """
    Generate a polar subplot with specific theta_offset.
    
    This function creates polar subplots with specified theta_offset and checks for collision.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    projection (str): The projection type for the subplot, set to 'polar'.
    theta_offset (int): The theta offset for the subplot, used to differentiate between subplots.
    
    Note:
    - Two subplots with the same theta_offset will collide and share the same axis.
    - Subplots with different
    """

    ax1 = plt.subplot(projection='polar', theta_offset=0)
    ax2 = plt.subplot(projection='polar', theta_offset=0)
    assert ax1 is ax2
    ax1.remove()
    ax3 = plt.subplot(projection='polar', theta_offset=1)
    assert ax1 is not ax3
    assert ax1 not in plt.gcf().axes


def test_gca():
    """
    Get the current axes.
    
    This function returns the current axes. If there are no axes, it creates a new figure and returns its axes. The function does not accept any parameters and does not return any value. It is used to ensure that there is always an active axes object for plotting.
    
    Key Points:
    - If there are no axes, a new figure is created and its axes is returned.
    - If there are existing axes, the same axes object is returned.
    - This function is useful for ensuring
    """

    # plt.gca() returns an existing axes, unless there were no axes.
    plt.figure()
    ax = plt.gca()
    ax1 = plt.gca()
    assert ax is not None
    assert ax1 is ax
    plt.close()


def test_subplot_projection_reuse():
    # create an Axes
    ax1 = plt.subplot(111)
    # check that it is current
    assert ax1 is plt.gca()
    # make sure we get it back if we ask again
    assert ax1 is plt.subplot(111)
    # remove it
    ax1.remove()
    # create a polar plot
    ax2 = plt.subplot(111, projection='polar')
    assert ax2 is plt.gca()
    # this should have deleted the first axes
    assert ax1 not in plt.gcf().axes
    # assert we get it back if no extra parameters passed
    assert ax2 is plt.subplot(111)
    ax2.remove()
    # now check explicitly setting the projection to rectilinear
    # makes a new axes
    ax3 = plt.subplot(111, projection='rectilinear')
    assert ax3 is plt.gca()
    assert ax3 is not ax2
    assert ax2 not in plt.gcf().axes


def test_subplot_polar_normalization():
    """
    Test subplot polar normalization.
    
    This function checks the behavior of creating polar subplots with different
    parameters and ensures that the correct subplot is returned. It also tests
    that an error is raised when attempting to create a polar subplot with a
    projection other than 'polar'.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the returned subplot objects are not as expected.
    ValueError: If a polar subplot is created with a projection other than 'polar'.
    """

    ax1 = plt.subplot(111, projection='polar')
    ax2 = plt.subplot(111, polar=True)
    ax3 = plt.subplot(111, polar=True, projection='polar')
    assert ax1 is ax2
    assert ax1 is ax3

    with pytest.raises(ValueError,
                       match="polar=True, yet projection='3d'"):
        ax2 = plt.subplot(111, polar=True, projection='3d')


def test_subplot_change_projection():
    created_axes = set()
    ax = plt.subplot()
    created_axes.add(ax)
    projections = ('aitoff', 'hammer', 'lambert', 'mollweide',
                   'polar', 'rectilinear', '3d')
    for proj in projections:
        ax.remove()
        ax = plt.subplot(projection=proj)
        assert ax is plt.subplot()
        assert ax.name == proj
        created_axes.add(ax)
    # Check that each call created a new Axes.
    assert len(created_axes) == 1 + len(projections)


def test_polar_second_call():
    # the first call creates the axes with polar projection
    ln1, = plt.polar(0., 1., 'ro')
    assert isinstance(ln1, mpl.lines.Line2D)
    # the second call should reuse the existing axes
    ln2, = plt.polar(1.57, .5, 'bo')
    assert isinstance(ln2, mpl.lines.Line2D)
    assert ln1.axes is ln2.axes


def test_fallback_position():
    # check that position kwarg works if rect not supplied
    axref = plt.axes([0.2, 0.2, 0.5, 0.5])
    axtest = plt.axes(position=[0.2, 0.2, 0.5, 0.5])
    np.testing.assert_allclose(axtest.bbox.get_points(),
                               axref.bbox.get_points())

    # check that position kwarg ignored if rect is supplied
    axref = plt.axes([0.2, 0.2, 0.5, 0.5])
    axtest = plt.axes([0.2, 0.2, 0.5, 0.5], position=[0.1, 0.1, 0.8, 0.8])
    np.testing.assert_allclose(axtest.bbox.get_points(),
                               axref.bbox.get_points())


def test_set_current_figure_via_subfigure():
    fig1 = plt.figure()
    subfigs = fig1.subfigures(2)

    plt.figure()
    assert plt.gcf() != fig1

    current = plt.figure(subfigs[1])
    assert plt.gcf() == fig1
    assert current == fig1


def test_set_current_axes_on_subfigure():
    """
    Set the current axes to a specific subplot within a subfigure.
    
    This function demonstrates how to set the current axes to a subplot within a subfigure in a matplotlib figure.
    
    Parameters:
    fig (Figure): The matplotlib figure object containing the subfigures.
    
    Returns:
    None: This function does not return any value. It modifies the current axes in the matplotlib state.
    
    Key Steps:
    1. Create a matplotlib figure object.
    2. Create subfigures within the figure.
    3. Create subplots within the
    """

    fig = plt.figure()
    subfigs = fig.subfigures(2)

    ax = subfigs[0].subplots(1, squeeze=True)
    subfigs[1].subplots(1, squeeze=True)

    assert plt.gca() != ax
    plt.sca(ax)
    assert plt.gca() == ax


def test_pylab_integration():
    """
    Test integration with the PyLab feature of IPython.
    
    This function checks if the IPython environment is correctly configured to use PyLab. It starts an IPython session with the --pylab option and verifies that the matplotlib.pyplot module's display hook is set to the expected value for IPython.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `pytest.importorskip` to ensure that the IPython package is available.
    - The test runs a subprocess to start an IPython
    """

    IPython = pytest.importorskip("IPython")
    mpl.testing.subprocess_run_helper(
        IPython.start_ipython,
        "--pylab",
        "-c",
        ";".join((
            "import matplotlib.pyplot as plt",
            "assert plt._REPL_DISPLAYHOOK == plt._ReplDisplayHook.IPYTHON",
        )),
        timeout=60,
    )


def test_doc_pyplot_summary():
    """Test that pyplot_summary lists all the plot functions."""
    pyplot_docs = Path(__file__).parent / '../../../doc/api/pyplot_summary.rst'
    if not pyplot_docs.exists():
        pytest.skip("Documentation sources not available")

    lines = pyplot_docs.read_text()
    m = re.search(r':nosignatures:\n\n(.*?)\n\n', lines, re.DOTALL)
    doc_functions = set(line.strip() for line in m.group(1).split('\n'))
    plot_commands = set(plt.get_plot_commands())
    missing = plot_commands.difference(doc_functions)
    if missing:
        raise AssertionError(
            f"The following pyplot functions are not listed in the "
            f"documentation. Please add them to doc/api/pyplot_summary.rst: "
            f"{missing!r}")
    extra = doc_functions.difference(plot_commands)
    if extra:
        raise AssertionError(
            f"The following functions are listed in the pyplot documentation, "
            f"but they do not exist in pyplot. "
            f"Please remove them from doc/api/pyplot_summary.rst: {extra!r}")
