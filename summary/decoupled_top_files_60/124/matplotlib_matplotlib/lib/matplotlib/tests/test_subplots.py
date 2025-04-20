import itertools

import numpy as np
import pytest

import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison
import matplotlib.axes as maxes


def check_shared(axs, x_shared, y_shared):
    """
    x_shared and y_shared are n x n boolean matrices; entry (i, j) indicates
    whether the x (or y) axes of subplots i and j should be shared.
    """
    for (i1, ax1), (i2, ax2), (i3, (name, shared)) in itertools.product(
            enumerate(axs),
            enumerate(axs),
            enumerate(zip("xy", [x_shared, y_shared]))):
        if i2 <= i1:
            continue
        assert axs[0]._shared_axes[name].joined(ax1, ax2) == shared[i1, i2], \
            "axes %i and %i incorrectly %ssharing %s axis" % (
                i1, i2, "not " if shared[i1, i2] else "", name)


def check_visible(axs, x_visible, y_visible):
    for i, (ax, vx, vy) in enumerate(zip(axs, x_visible, y_visible)):
        for l in ax.get_xticklabels() + [ax.xaxis.offsetText]:
            assert l.get_visible() == vx, \
                    f"Visibility of x axis #{i} is incorrectly {vx}"
        for l in ax.get_yticklabels() + [ax.yaxis.offsetText]:
            assert l.get_visible() == vy, \
                    f"Visibility of y axis #{i} is incorrectly {vy}"
        # axis label "visibility" is toggled by label_outer by resetting the
        # label to empty, but it can also be empty to start with.
        if not vx:
            assert ax.get_xlabel() == ""
        if not vy:
            assert ax.get_ylabel() == ""


def test_shared():
    """
    Test different sharing options for subplots.
    
    This function creates subplots with various sharing options and checks if the sharing
    and visibility of the axes labels are as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Options:
    - `share`: A dictionary containing sharing configurations for the x and y axes.
    - `visible`: A dictionary containing expected visibility configurations for the x and y axes.
    
    Test Cases:
    - Default sharing (no sharing).
    - All sharing options for x and
    """

    rdim = (4, 4, 2)
    share = {
            'all': np.ones(rdim[:2], dtype=bool),
            'none': np.zeros(rdim[:2], dtype=bool),
            'row': np.array([
                [False, True, False, False],
                [True, False, False, False],
                [False, False, False, True],
                [False, False, True, False]]),
            'col': np.array([
                [False, False, True, False],
                [False, False, False, True],
                [True, False, False, False],
                [False, True, False, False]]),
            }
    visible = {
            'x': {
                'all': [False, False, True, True],
                'col': [False, False, True, True],
                'row': [True] * 4,
                'none': [True] * 4,
                False: [True] * 4,
                True: [False, False, True, True],
                },
            'y': {
                'all': [True, False, True, False],
                'col': [True] * 4,
                'row': [True, False, True, False],
                'none': [True] * 4,
                False: [True] * 4,
                True: [True, False, True, False],
                },
            }
    share[False] = share['none']
    share[True] = share['all']

    # test default
    f, ((a1, a2), (a3, a4)) = plt.subplots(2, 2)
    axs = [a1, a2, a3, a4]
    check_shared(axs, share['none'], share['none'])
    plt.close(f)

    # test all option combinations
    ops = [False, True, 'all', 'none', 'row', 'col']
    for xo in ops:
        for yo in ops:
            f, ((a1, a2), (a3, a4)) = plt.subplots(2, 2, sharex=xo, sharey=yo)
            axs = [a1, a2, a3, a4]
            check_shared(axs, share[xo], share[yo])
            check_visible(axs, visible['x'][xo], visible['y'][yo])
            plt.close(f)

    # test label_outer
    f, ((a1, a2), (a3, a4)) = plt.subplots(2, 2, sharex=True, sharey=True)
    axs = [a1, a2, a3, a4]
    for ax in axs:
        ax.set(xlabel="foo", ylabel="bar")
        ax.label_outer()
    check_visible(axs, [False, False, True, True], [True, False, True, False])


def test_label_outer_span():
    fig = plt.figure()
    gs = fig.add_gridspec(3, 3)
    # +---+---+---+
    # |   1   |   |
    # +---+---+---+
    # |   |   | 3 |
    # + 2 +---+---+
    # |   | 4 |   |
    # +---+---+---+
    a1 = fig.add_subplot(gs[0, 0:2])
    a2 = fig.add_subplot(gs[1:3, 0])
    a3 = fig.add_subplot(gs[1, 2])
    a4 = fig.add_subplot(gs[2, 1])
    for ax in fig.axes:
        ax.label_outer()
    check_visible(
        fig.axes, [False, True, False, True], [True, True, False, False])


def test_shared_and_moved():
    """
    Test the behavior of shared axes when modifying tick positions.
    
    This function checks the visibility of y-axis and x-axis labels when
    the `sharey` and `sharex` parameters are set to `True` and the tick positions
    are modified using `yaxis.tick_left()` and `xaxis.tick_bottom()`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function creates subplots with shared y-axes or x-axes.
    - It then checks the
    """

    # test if sharey is on, but then tick_left is called that labels don't
    # re-appear.  Seaborn does this just to be sure yaxis is on left...
    f, (a1, a2) = plt.subplots(1, 2, sharey=True)
    check_visible([a2], [True], [False])
    a2.yaxis.tick_left()
    check_visible([a2], [True], [False])

    f, (a1, a2) = plt.subplots(2, 1, sharex=True)
    check_visible([a1], [False], [True])
    a2.xaxis.tick_bottom()
    check_visible([a1], [False], [True])


def test_exceptions():
    # TODO should this test more options?
    with pytest.raises(ValueError):
        plt.subplots(2, 2, sharex='blah')
    with pytest.raises(ValueError):
        plt.subplots(2, 2, sharey='blah')


@image_comparison(['subplots_offset_text'])
def test_subplots_offsettext():
    x = np.arange(0, 1e10, 1e9)
    y = np.arange(0, 100, 10)+1e4
    fig, axs = plt.subplots(2, 2, sharex='col', sharey='all')
    axs[0, 0].plot(x, x)
    axs[1, 0].plot(x, x)
    axs[0, 1].plot(y, x)
    axs[1, 1].plot(y, x)


@pytest.mark.parametrize("top", [True, False])
@pytest.mark.parametrize("bottom", [True, False])
@pytest.mark.parametrize("left", [True, False])
@pytest.mark.parametrize("right", [True, False])
def test_subplots_hide_ticklabels(top, bottom, left, right):
    """
    Hide or show tick labels on subplots.
    
    This function creates a 3x3 grid of subplots and adjusts the visibility of
    the tick labels based on the provided parameters. The function uses the
    matplotlib library to create the subplots and set the tick label visibility.
    
    Parameters:
    top (bool): Whether to hide or show the top x-axis tick labels.
    bottom (bool): Whether to hide or show the bottom x-axis tick labels.
    left (bool): Whether to hide or
    """

    # Ideally, we would also test offset-text visibility (and remove
    # test_subplots_offsettext), but currently, setting rcParams fails to move
    # the offset texts as well.
    with plt.rc_context({"xtick.labeltop": top, "xtick.labelbottom": bottom,
                         "ytick.labelleft": left, "ytick.labelright": right}):
        axs = plt.figure().subplots(3, 3, sharex=True, sharey=True)
    for (i, j), ax in np.ndenumerate(axs):
        xtop = ax.xaxis._major_tick_kw["label2On"]
        xbottom = ax.xaxis._major_tick_kw["label1On"]
        yleft = ax.yaxis._major_tick_kw["label1On"]
        yright = ax.yaxis._major_tick_kw["label2On"]
        assert xtop == (top and i == 0)
        assert xbottom == (bottom and i == 2)
        assert yleft == (left and j == 0)
        assert yright == (right and j == 2)


@pytest.mark.parametrize("xlabel_position", ["bottom", "top"])
@pytest.mark.parametrize("ylabel_position", ["left", "right"])
def test_subplots_hide_axislabels(xlabel_position, ylabel_position):
    """
    Generate subplots with custom axis labels positions.
    
    This function creates a 3x3 grid of subplots and customizes the positions of
    the x and y axis labels. The labels are hidden or shown based on the specified
    positions.
    
    Parameters:
    xlabel_position (str): The position of the x-axis labels. Can be 'bottom' or 'top'.
    ylabel_position (str): The position of the y-axis labels. Can be 'left' or 'right'.
    
    Returns:
    None
    """

    axs = plt.figure().subplots(3, 3, sharex=True, sharey=True)
    for (i, j), ax in np.ndenumerate(axs):
        ax.set(xlabel="foo", ylabel="bar")
        ax.xaxis.set_label_position(xlabel_position)
        ax.yaxis.set_label_position(ylabel_position)
        ax.label_outer()
        assert bool(ax.get_xlabel()) == (
            xlabel_position == "bottom" and i == 2
            or xlabel_position == "top" and i == 0)
        assert bool(ax.get_ylabel()) == (
            ylabel_position == "left" and j == 0
            or ylabel_position == "right" and j == 2)


def test_get_gridspec():
    # ahem, pretty trivial, but...
    fig, ax = plt.subplots()
    assert ax.get_subplotspec().get_gridspec() == ax.get_gridspec()


def test_dont_mutate_kwargs():
    """
    Create a figure with subplots using specified subplot and gridspec keyword arguments.
    
    This function initializes a figure with two subplots and ensures that the keyword arguments for subplot and gridspec are not mutated.
    
    Parameters:
    None
    
    Returns:
    tuple: A tuple containing the figure object and a list of axes objects.
    
    Key Parameters:
    subplot_kw (dict, optional): Keyword arguments for the subplots. Defaults to {'sharex': 'all'}.
    gridspec_kw (dict, optional): Keyword
    """

    subplot_kw = {'sharex': 'all'}
    gridspec_kw = {'width_ratios': [1, 2]}
    fig, ax = plt.subplots(1, 2, subplot_kw=subplot_kw,
                           gridspec_kw=gridspec_kw)
    assert subplot_kw == {'sharex': 'all'}
    assert gridspec_kw == {'width_ratios': [1, 2]}


def test_subplot_factory_reapplication():
    assert maxes.subplot_class_factory(maxes.Axes) is maxes.Subplot
    assert maxes.subplot_class_factory(maxes.Subplot) is maxes.Subplot
plot_class_factory(maxes.Subplot) is maxes.Subplot
