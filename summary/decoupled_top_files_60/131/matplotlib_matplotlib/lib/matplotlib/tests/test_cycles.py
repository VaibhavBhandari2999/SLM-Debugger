import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from cycler import cycler


def test_colorcycle_basic():
    """
    Test the basic functionality of the color cycle.
    
    This function creates a simple plot with multiple lines, each with a different color
    from a predefined cycle, and checks that the colors are applied correctly.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    None
    
    Assertions:
    - The list of colors of the lines in the plot should match ['r', 'g', 'y', 'r'].
    """

    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler('color', ['r', 'g', 'y']))
    for _ in range(4):
        ax.plot(range(10), range(10))
    assert [l.get_color() for l in ax.lines] == ['r', 'g', 'y', 'r']


def test_marker_cycle():
    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler('c', ['r', 'g', 'y']) +
                      cycler('marker', ['.', '*', 'x']))
    for _ in range(4):
        ax.plot(range(10), range(10))
    assert [l.get_color() for l in ax.lines] == ['r', 'g', 'y', 'r']
    assert [l.get_marker() for l in ax.lines] == ['.', '*', 'x', '.']


def test_marker_cycle_kwargs_arrays_iterators():
    fig, ax = plt.subplots()
    ax.set_prop_cycle(c=np.array(['r', 'g', 'y']),
                      marker=iter(['.', '*', 'x']))
    for _ in range(4):
        ax.plot(range(10), range(10))
    assert [l.get_color() for l in ax.lines] == ['r', 'g', 'y', 'r']
    assert [l.get_marker() for l in ax.lines] == ['.', '*', 'x', '.']


def test_linestylecycle_basic():
    """
    Test the basic functionality of the linestyle cycle.
    
    This function creates a plot with four lines, each with a different line style
    from a predefined cycle. The cycle is set using `set_prop_cycle` with a cycler
    on the line style ('ls'). The function asserts that the line styles of the
    plotted lines match the expected sequence.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    None
    
    Note:
    The function uses matplotlib to create the plot and perform the assertion
    """

    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler('ls', ['-', '--', ':']))
    for _ in range(4):
        ax.plot(range(10), range(10))
    assert [l.get_linestyle() for l in ax.lines] == ['-', '--', ':', '-']


def test_fillcycle_basic():
    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler('c',  ['r', 'g', 'y']) +
                      cycler('hatch', ['xx', 'O', '|-']) +
                      cycler('linestyle', ['-', '--', ':']))
    for _ in range(4):
        ax.fill(range(10), range(10))
    assert ([p.get_facecolor() for p in ax.patches]
            == [mpl.colors.to_rgba(c) for c in ['r', 'g', 'y', 'r']])
    assert [p.get_hatch() for p in ax.patches] == ['xx', 'O', '|-', 'xx']
    assert [p.get_linestyle() for p in ax.patches] == ['-', '--', ':', '-']


def test_fillcycle_ignore():
    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler('color',  ['r', 'g', 'y']) +
                      cycler('hatch', ['xx', 'O', '|-']) +
                      cycler('marker', ['.', '*', 'D']))
    t = range(10)
    # Should not advance the cycler, even though there is an
    # unspecified property in the cycler "marker".
    # "marker" is not a Polygon property, and should be ignored.
    ax.fill(t, t, 'r', hatch='xx')
    # Allow the cycler to advance, but specify some properties
    ax.fill(t, t, hatch='O')
    ax.fill(t, t)
    ax.fill(t, t)
    assert ([p.get_facecolor() for p in ax.patches]
            == [mpl.colors.to_rgba(c) for c in ['r', 'r', 'g', 'y']])
    assert [p.get_hatch() for p in ax.patches] == ['xx', 'O', 'O', '|-']


def test_property_collision_plot():
    """
    Generate a property cycle collision plot.
    
    This function creates a plot with multiple lines, each with a different linewidth,
    demonstrating the behavior of the `set_prop_cycle` method in matplotlib. The function
    sets the line width cycle and then plots lines with specified linewidths, followed by
    additional lines with default linewidths.
    
    Parameters:
    None
    
    Returns:
    fig, ax: A matplotlib Figure and Axes object containing the plot.
    """

    fig, ax = plt.subplots()
    ax.set_prop_cycle('linewidth', [2, 4])
    t = range(10)
    for c in range(1, 4):
        ax.plot(t, t, lw=0.1)
    ax.plot(t, t)
    ax.plot(t, t)
    assert [l.get_linewidth() for l in ax.lines] == [0.1, 0.1, 0.1, 2, 4]


def test_property_collision_fill():
    fig, ax = plt.subplots()
    ax.set_prop_cycle(linewidth=[2, 3, 4, 5, 6], facecolor='bgcmy')
    t = range(10)
    for c in range(1, 4):
        ax.fill(t, t, lw=0.1)
    ax.fill(t, t)
    ax.fill(t, t)
    assert ([p.get_facecolor() for p in ax.patches]
            == [mpl.colors.to_rgba(c) for c in 'bgcmy'])
    assert [p.get_linewidth() for p in ax.patches] == [0.1, 0.1, 0.1, 5, 6]


def test_valid_input_forms():
    """
    Test valid input forms for set_prop_cycle.
    
    This function checks various valid forms of input for the set_prop_cycle method
    of an Axes object. It ensures that the method can handle different types of
    input for cycle properties such as 'linewidth', 'color', 'dashes', and custom
    keyword arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Input Forms:
    - None
    - Single property with a list of values
    - Single property with an iterable of values
    """

    fig, ax = plt.subplots()
    # These should not raise an error.
    ax.set_prop_cycle(None)
    ax.set_prop_cycle(cycler('linewidth', [1, 2]))
    ax.set_prop_cycle('color', 'rgywkbcm')
    ax.set_prop_cycle('lw', (1, 2))
    ax.set_prop_cycle('linewidth', [1, 2])
    ax.set_prop_cycle('linewidth', iter([1, 2]))
    ax.set_prop_cycle('linewidth', np.array([1, 2]))
    ax.set_prop_cycle('color', np.array([[1, 0, 0],
                                         [0, 1, 0],
                                         [0, 0, 1]]))
    ax.set_prop_cycle('dashes', [[], [13, 2], [8, 3, 1, 3]])
    ax.set_prop_cycle(lw=[1, 2], color=['k', 'w'], ls=['-', '--'])
    ax.set_prop_cycle(lw=np.array([1, 2]),
                      color=np.array(['k', 'w']),
                      ls=np.array(['-', '--']))


def test_cycle_reset():
    fig, ax = plt.subplots()

    # Can't really test a reset because only a cycle object is stored
    # but we can test the first item of the cycle.
    prop = next(ax._get_lines.prop_cycler)
    ax.set_prop_cycle(linewidth=[10, 9, 4])
    assert prop != next(ax._get_lines.prop_cycler)
    ax.set_prop_cycle(None)
    got = next(ax._get_lines.prop_cycler)
    assert prop == got


def test_invalid_input_forms():
    """
    Test invalid input forms for setting property cycles.
    
    This function checks various invalid input forms for the `set_prop_cycle` method
    of a matplotlib Axes object. It raises appropriate exceptions for different
    invalid inputs.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError, ValueError: Raised when an invalid input is provided to `set_prop_cycle`.
    """

    fig, ax = plt.subplots()

    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle(1)
    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle([1, 2])

    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle('color', 'fish')

    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle('linewidth', 1)
    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle('linewidth', {1, 2})
    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle(linewidth=1, color='r')

    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle('foobar', [1, 2])
    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle(foobar=[1, 2])

    with pytest.raises((TypeError, ValueError)):
        ax.set_prop_cycle(cycler(foobar=[1, 2]))
    with pytest.raises(ValueError):
        ax.set_prop_cycle(cycler(color='rgb', c='cmy'))
