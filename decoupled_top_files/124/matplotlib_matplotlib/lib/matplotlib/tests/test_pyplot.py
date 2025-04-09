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
    Generates a Python docstring for the provided function.
    
    Args:
    tmpdir (str): A temporary directory path where the modified pyplot file will be saved.
    
    Returns:
    None: The function updates the `pyplot.py` file in place and does not return any value.
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
    """
    Wrapper function for `func` with deprecated parameters.
    
    Parameters
    ----------
    new : {None}
    The new parameter.
    kwo : {None}, keyword-only
    The keyword-only parameter.
    
    Warnings
    --------
    This function is deprecated and will be removed in a future version.
    Use the `new` parameter instead of the `old` parameter.
    """

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
    """
    Control the display of the axes border.
    
    This function toggles the visibility of the axes border using the `box`
    parameter. It asserts whether the frame is on or off after each call to
    `plt.box()`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example Usage:
    >>> test_pyplot_box()
    """

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
    Raise TypeError when nrows or ncols is specified in plt.subplot.
    
    This function tests whether specifying `nrows` or `ncols` arguments
    in `plt.subplot` raises a TypeError. It checks both `nrows` and `ncols`
    to ensure that only the `num` argument is accepted for this function.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If `nrows` or `ncols` is specified in `plt
    """

    with pytest.raises(TypeError):
        plt.subplot(nrows=1)
    with pytest.raises(TypeError):
        plt.subplot(ncols=1)


def test_ioff():
    """
    Switch to interactive mode, check if interactive mode is active, and revert to non-interactive mode.
    
    This function demonstrates the usage of `plt.ion()` and `plt.ioff()` to toggle between interactive and non-interactive modes in Matplotlib. It also verifies the state of interactive mode using `mpl.is_interactive()`.
    
    Usage:
    test_ioff()
    
    Effects:
    - Switches to interactive mode using `plt.ion()`.
    - Verifies that interactive mode is
    """

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
    """
    Disable interactive mode, check if interactive mode is off, enable interactive mode within a context manager, check if interactive mode is on, and then revert to non-interactive mode. Additionally, demonstrate the behavior of `plt.ion()` both outside and inside a context manager, ensuring that the state of interactive mode remains consistent after each operation.
    """

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
    Test the interaction between `plt.ion()` and `plt.ioff()`.
    
    This function checks how the `plt.ion()` and `plt.ioff()` functions
    affect the interactive mode of Matplotlib, both when the initial
    state is interactive and when it is not. It uses context managers
    to ensure that the state is properly restored after each test case.
    
    Keywords:
    - `plt.ion()`: Enables interactive mode.
    - `plt.ioff()
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
    """
    Close a figure.
    
    This function attempts to close a figure with a specified identifier. If the identifier is invalid or of incorrect type, a `TypeError` is raised with a specific error message.
    
    Parameters:
    None
    
    Raises:
    TypeError: If the close() argument is not a valid Figure, integer, string, or None.
    
    Example:
    >>> test_close()
    AssertionError: close() argument must be a Figure, an int, a string, or None, not <class
    """

    try:
        plt.close(1.1)
    except TypeError as e:
        assert str(e) == "close() argument must be a Figure, an int, " \
                         "a string, or None, not <class 'float'>"


def test_subplot_reuse():
    """
    Create subplots and verify their reuse.
    
    This function creates two subplots using `plt.subplot` and checks if
    subsequent calls to `plt.subplot` with the same index return the
    previously created axes object. The important functions used are
    `plt.subplot`, `plt.gca`, and the axes objects `ax1` and `ax2`.
    
    Args:
    None
    
    Returns:
    None
    """

    ax1 = plt.subplot(121)
    assert ax1 is plt.gca()
    ax2 = plt.subplot(122)
    assert ax2 is plt.gca()
    ax3 = plt.subplot(121)
    assert ax1 is plt.gca()
    assert ax1 is ax3


def test_axes_kwargs():
    """
    Test the creation of axes with different projection types.
    
    This function checks that `plt.axes()` creates distinct axes objects
    when called multiple times with or without specifying the projection
    type. It ensures that the axes are properly initialized and that their
    names reflect the specified projections.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `plt.figure()` to create new figure instances.
    - `plt.axes()` is used to create axes objects
    """

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
    """
    Create and manage subplots with different projections.
    
    This function demonstrates how `plt.subplot()` behaves when creating
    subplots with the same subplot specification but different projection
    types. It creates multiple subplots and verifies their existence,
    uniqueness, and projection type.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `pytest.warns` to capture deprecation warnings.
    - It creates a figure and several subplots with various subplot specifications.
    """

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
    Create subplot with polar projection and test for keyword argument collision.
    
    This function creates two subplots with polar projections and checks if they are the same object. It then removes one subplot, creates another with a different `theta_offset` value, and verifies that it is a new object and not associated with the previous subplot.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplot(projection='polar', theta_offset=<value>)`: Creates a subplot
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
    Get the current axes (or create one if none exist).
    
    This function retrieves the current axes object from the current figure.
    If no axes exist, it creates one. The function asserts that the first and
    second calls to `plt.gca()` return the same axes object.
    
    Parameters:
    None
    
    Returns:
    ax (matplotlib.axes.Axes): The current axes object.
    
    Example:
    >>> import matplotlib.pyplot as plt
    >>> test_gca()
    """

    # plt.gca() returns an existing axes, unless there were no axes.
    plt.figure()
    ax = plt.gca()
    ax1 = plt.gca()
    assert ax is not None
    assert ax1 is ax
    plt.close()


def test_subplot_projection_reuse():
    """
    Create and manipulate subplots with different projections.
    
    This function demonstrates the creation and management of subplots with
    various projections, including checking the current axes, removing axes,
    and ensuring proper reuse of subplot indices.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `plt.subplot`: Create a subplot with specified dimensions and projection.
    - `plt.gca()`: Get the current axes.
    - `ax.remove()`: Remove an axes from the
    """

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
    Create subplots with polar projections and verify their equivalence.
    
    This function generates three subplots with polar projections using different
    initialization methods and asserts that they are equivalent. It also tests
    whether a ValueError is raised when attempting to create a subplot with both
    `polar=True` and `projection='3d'`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplot`: Creates a subplot with specified parameters.
    - `assert
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
    """
    Create a series of subplots with different projections.
    
    This function creates a subplot and then changes its projection to various
    types, including 'aitoff', 'hammer', 'lambert', 'mollweide', 'polar',
    'rectilinear', and '3d'. It ensures that each subplot is unique by removing
    the previous one before creating a new one with the specified projection.
    The function also checks that the created axes are correctly named and
    stored
    """

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
    """
    Create two line plots on a polar axis using the `polar` function.
    
    This function generates two line plots on a polar axis. The first plot is created by calling `plt.polar` with initial angle and radius values, followed by a red circle marker. The second plot is created by calling `plt.polar` again with different angle and radius values, followed by a blue circle marker. Both lines are expected to be instances of `mpl.lines.Line2D`, and the axes used
    """

    # the first call creates the axes with polar projection
    ln1, = plt.polar(0., 1., 'ro')
    assert isinstance(ln1, mpl.lines.Line2D)
    # the second call should reuse the existing axes
    ln2, = plt.polar(1.57, .5, 'bo')
    assert isinstance(ln2, mpl.lines.Line2D)
    assert ln1.axes is ln2.axes


def test_fallback_position():
    """
    Create axes with specified position.
    
    This function creates an axes object with the given position using either
    the `position` or `rect` keyword arguments. The `position` argument takes
    a list of four floats representing the left, bottom, width, and height of
    the axes, while the `rect` argument takes a list of two floats representing
    the width and height of the axes, with the origin at the lower-left corner
    of the figure.
    
    Parameters
    """

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
    """
    Set the current figure via a subfigure.
    
    This function demonstrates how to set the current figure using a subfigure
    obtained from a parent figure. It creates a parent figure, adds two subfigures,
    and then switches the current figure to one of the subfigures.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `plt.figure`: Creates a new figure or activates an existing one.
    - `fig1.subfigures(2)`:
    """

    fig1 = plt.figure()
    subfigs = fig1.subfigures(2)

    plt.figure()
    assert plt.gcf() != fig1

    current = plt.figure(subfigs[1])
    assert plt.gcf() == fig1
    assert current == fig1


def test_set_current_axes_on_subfigure():
    """
    Set the current axes on a subfigure.
    
    This function creates a figure with two subfigures and plots an axis on the first subfigure. It then checks if the current axes is set correctly and sets it explicitly using `plt.sca()`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `plt.figure()`: Creates a new figure.
    - `fig.subfigures(nrows, ncols)`: Divides the figure into subfigures.
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
    Test the integration of PyLab with IPython.
    
    This function checks if PyLab is correctly integrated with IPython by starting an IPython session with the `--pylab` flag and running specific commands to verify the expected behavior.
    
    Args:
    None
    
    Returns:
    None
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
