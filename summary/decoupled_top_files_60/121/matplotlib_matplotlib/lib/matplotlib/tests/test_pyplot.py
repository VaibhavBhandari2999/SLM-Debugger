import difflib
import numpy as np
import subprocess
import sys
from pathlib import Path

import pytest

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib._api import MatplotlibDeprecationWarning


def test_pyplot_up_to_date(tmpdir):
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
    Generate a Python docstring for the provided function.
    
    Parameters:
    func (function): The function for which to generate the docstring.
    
    Returns:
    str: The generated docstring.
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
    Test the functionality of the `plt.box()` method in matplotlib.
    
    This function checks the behavior of the `plt.box()` method, which controls the display of the box around the plot. The method can accept three types of arguments: 'on', 'off', and no argument.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key behaviors tested:
    - Setting the box on and off using `plt.box(True)` and `plt.box(False)`.
    - Setting the box state to the default using `plt.box
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
    Test the interaction between 'ion' and 'ioff' context managers for managing interactive mode in Matplotlib.
    
    This function checks the behavior of the 'ion' and 'ioff' context managers, which control whether Matplotlib figures are displayed interactively or not. The function tests various combinations of 'ion' and 'ioff' to ensure they work as expected.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Input:
    - None
    
    Output:
    - None
    
    Behavior:
    - The
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
    Test the behavior of the `plt.close` function with a non-integer, non-string, non-Figure object.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If the argument passed to `plt.close` is not a valid type (Figure, int, string, or None).
    
    This function attempts to close a figure using a float as an argument and asserts that a TypeError is raised with the expected error message.
    """

    try:
        plt.close(1.1)
    except TypeError as e:
        assert str(e) == "close() argument must be a Figure, an int, " \
                         "a string, or None, not <class 'float'>"


def test_subplot_reuse():
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
    """
    Create and manage subplots with projection.
    
    This function creates subplots in a figure, searching for existing axes with
    the same subplot specification and projection. If an existing axes with the
    same subplot specification and projection is found, it is returned. If not,
    a new axes is created. The function also issues a deprecation warning when
    creating a subplot with a polar projection.
    
    Parameters:
    fig (Figure): The figure to which the subplot will be added.
    subplot_spec (SubplotSpec
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
    ax1 = plt.subplot(projection='polar', theta_offset=0)
    ax2 = plt.subplot(projection='polar', theta_offset=0)
    assert ax1 is ax2
    ax1.remove()
    ax3 = plt.subplot(projection='polar', theta_offset=1)
    assert ax1 is not ax3
    assert ax1 not in plt.gcf().axes


def test_gca_kwargs():
    """
    Generate a new axes if none exist, or return the existing one. The function `test_gca_kwargs` creates and manipulates figures and axes to demonstrate the behavior of `plt.gca()` with and without keyword arguments.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - projection: A keyword argument to specify the projection type of the axes.
    
    Input:
    - None
    
    Output:
    - None
    
    Behavior:
    1. Creates a new figure and checks if `plt.gca()` returns an existing axes or creates a
    """

    # plt.gca() returns an existing axes, unless there were no axes.
    plt.figure()
    ax = plt.gca()
    ax1 = plt.gca()
    assert ax is not None
    assert ax1 is ax
    plt.close()

    # plt.gca() raises a DeprecationWarning if called with kwargs.
    plt.figure()
    with pytest.warns(
            MatplotlibDeprecationWarning,
            match=r'Calling gca\(\) with keyword arguments was deprecated'):
        ax = plt.gca(projection='polar')
    ax1 = plt.gca()
    assert ax is not None
    assert ax1 is ax
    assert ax1.name == 'polar'
    plt.close()

    # plt.gca() ignores keyword arguments if an Axes already exists.
    plt.figure()
    ax = plt.gca()
    with pytest.warns(
            MatplotlibDeprecationWarning,
            match=r'Calling gca\(\) with keyword arguments was deprecated'):
        ax1 = plt.gca(projection='polar')
    assert ax is not None
    assert ax1 is ax
    assert ax1.name == 'rectilinear'
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
    
    This function checks the behavior of creating subplots with polar projection
    using different initialization methods and ensures that the created subplots
    are the same object. It also tests the error handling when trying to create
    a polar subplot with a 3D projection.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If a polar subplot is created with a 3D projection.
    
    Usage:
    test_subplot_polar_normalization()
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
    """
    Test that plt.polar() reuses axes on second call.
    
    This function checks that the `plt.polar()` function creates the axes with a polar projection on the first call and reuses the existing axes on the second call. It asserts that the returned line objects are instances of `mpl.lines.Line2D` and that the axes of the two line objects are the same.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The first call to `plt.polar()` creates axes with a
    """

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
