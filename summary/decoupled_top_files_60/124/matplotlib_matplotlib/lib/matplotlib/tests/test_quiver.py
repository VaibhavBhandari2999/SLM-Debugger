import platform
import sys

import numpy as np
import pytest

from matplotlib import pyplot as plt
from matplotlib.testing.decorators import image_comparison


def draw_quiver(ax, **kwargs):
    """
    Draw a quiver plot.
    
    This function creates a quiver plot using the given axes (ax). The quiver plot
    is defined by the U and V arrays, which represent the vector components in the
    x and y directions, respectively. The function accepts various keyword
    arguments to customize the appearance of the quiver plot.
    
    Parameters:
    ax (matplotlib.axes.Axes): The axes object to plot on.
    **kwargs: Additional keyword arguments to customize the quiver plot.
    These can
    """

    X, Y = np.meshgrid(np.arange(0, 2 * np.pi, 1),
                       np.arange(0, 2 * np.pi, 1))
    U = np.cos(X)
    V = np.sin(Y)

    Q = ax.quiver(U, V, **kwargs)
    return Q


@pytest.mark.skipif(platform.python_implementation() != 'CPython',
                    reason='Requires CPython')
def test_quiver_memory_leak():
    fig, ax = plt.subplots()

    Q = draw_quiver(ax)
    ttX = Q.X
    Q.remove()

    del Q

    assert sys.getrefcount(ttX) == 2


@pytest.mark.skipif(platform.python_implementation() != 'CPython',
                    reason='Requires CPython')
def test_quiver_key_memory_leak():
    fig, ax = plt.subplots()

    Q = draw_quiver(ax)

    qk = ax.quiverkey(Q, 0.5, 0.92, 2, r'$2 \frac{m}{s}$',
                      labelpos='W',
                      fontproperties={'weight': 'bold'})
    assert sys.getrefcount(qk) == 3
    qk.remove()
    assert sys.getrefcount(qk) == 2


def test_quiver_number_of_args():
    """
    Function: test_quiver_number_of_args
    Summary: Tests the number of positional arguments passed to the quiver function in matplotlib.
    
    Parameters:
    X (list): A list of numeric values representing the x-coordinates.
    
    Returns:
    None: This function does not return any value. It raises a TypeError if the number of arguments is not within the expected range.
    
    Raises:
    TypeError: If the function is called with less than 2 or more than 5 positional arguments.
    """

    X = [1, 2]
    with pytest.raises(
            TypeError,
            match='takes 2-5 positional arguments but 1 were given'):
        plt.quiver(X)
    with pytest.raises(
            TypeError,
            match='takes 2-5 positional arguments but 6 were given'):
        plt.quiver(X, X, X, X, X, X)


def test_quiver_arg_sizes():
    """
    Test the size compatibility of arguments in the quiver function.
    
    This function checks the size compatibility of the input arguments for the
    `quiver` function. It raises a ValueError if the sizes of the arguments do not
    match as expected.
    
    Parameters:
    X2 (list): A list of size 2 representing the x-coordinates.
    X3 (list): A list of size 3 representing the y-coordinates.
    
    Raises:
    ValueError: If the sizes of X and Y do not
    """

    X2 = [1, 2]
    X3 = [1, 2, 3]
    with pytest.raises(
            ValueError, match=('X and Y must be the same size, but '
                               'X.size is 2 and Y.size is 3.')):
        plt.quiver(X2, X3, X2, X2)
    with pytest.raises(
            ValueError, match=('Argument U has a size 3 which does not match '
                               '2, the number of arrow positions')):
        plt.quiver(X2, X2, X3, X2)
    with pytest.raises(
            ValueError, match=('Argument V has a size 3 which does not match '
                               '2, the number of arrow positions')):
        plt.quiver(X2, X2, X2, X3)
    with pytest.raises(
            ValueError, match=('Argument C has a size 3 which does not match '
                               '2, the number of arrow positions')):
        plt.quiver(X2, X2, X2, X2, X3)


def test_no_warnings():
    fig, ax = plt.subplots()
    X, Y = np.meshgrid(np.arange(15), np.arange(10))
    U = V = np.ones_like(X)
    phi = (np.random.rand(15, 10) - .5) * 150
    ax.quiver(X, Y, U, V, angles=phi)
    fig.canvas.draw()  # Check that no warning is emitted.


def test_zero_headlength():
    # Based on report by Doug McNeil:
    # http://matplotlib.1069221.n5.nabble.com/quiver-warnings-td28107.html
    fig, ax = plt.subplots()
    X, Y = np.meshgrid(np.arange(10), np.arange(10))
    U, V = np.cos(X), np.sin(Y)
    ax.quiver(U, V, headlength=0, headaxislength=0)
    fig.canvas.draw()  # Check that no warning is emitted.


@image_comparison(['quiver_animated_test_image.png'])
def test_quiver_animate():
    """
    Tests fix for #2616.
    
    This function creates a quiver plot with animation support and includes a quiver key for reference.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the quiver plot.
    ax (matplotlib.axes.Axes): The axes object containing the quiver plot.
    
    Notes:
    - The quiver plot is created with animation support enabled.
    - A quiver key is added to the plot for reference.
    """

    # Tests fix for #2616
    fig, ax = plt.subplots()
    Q = draw_quiver(ax, animated=True)
    ax.quiverkey(Q, 0.5, 0.92, 2, r'$2 \frac{m}{s}$',
                 labelpos='W', fontproperties={'weight': 'bold'})


@image_comparison(['quiver_with_key_test_image.png'])
def test_quiver_with_key():
    fig, ax = plt.subplots()
    ax.margins(0.1)
    Q = draw_quiver(ax)
    ax.quiverkey(Q, 0.5, 0.95, 2,
                 r'$2\, \mathrm{m}\, \mathrm{s}^{-1}$',
                 angle=-10,
                 coordinates='figure',
                 labelpos='W',
                 fontproperties={'weight': 'bold', 'size': 'large'})


@image_comparison(['quiver_single_test_image.png'], remove_text=True)
def test_quiver_single():
    fig, ax = plt.subplots()
    ax.margins(0.1)
    ax.quiver([1], [1], [2], [2])


def test_quiver_copy():
    """
    Test the behavior of the quiver function when modifying input data.
    
    This function creates a quiver plot using the given initial vector data and checks if the quiver plot object retains the original vector data even after modifying the input data.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    fig (matplotlib.figure.Figure): The figure object containing the quiver plot.
    ax (matplotlib.axes.Axes): The axes object containing the quiver plot.
    uv (dict): A dictionary containing
    """

    fig, ax = plt.subplots()
    uv = dict(u=np.array([1.1]), v=np.array([2.0]))
    q0 = ax.quiver([1], [1], uv['u'], uv['v'])
    uv['v'][0] = 0
    assert q0.V[0] == 2.0


@image_comparison(['quiver_key_pivot.png'], remove_text=True)
def test_quiver_key_pivot():
    fig, ax = plt.subplots()

    u, v = np.mgrid[0:2*np.pi:10j, 0:2*np.pi:10j]

    q = ax.quiver(np.sin(u), np.cos(v))
    ax.set_xlim(-2, 11)
    ax.set_ylim(-2, 11)
    ax.quiverkey(q, 0.5, 1, 1, 'N', labelpos='N')
    ax.quiverkey(q, 1, 0.5, 1, 'E', labelpos='E')
    ax.quiverkey(q, 0.5, 0, 1, 'S', labelpos='S')
    ax.quiverkey(q, 0, 0.5, 1, 'W', labelpos='W')


@image_comparison(['quiver_key_xy.png'], remove_text=True)
def test_quiver_key_xy():
    # With scale_units='xy', ensure quiverkey still matches its quiver.
    # Note that the quiver and quiverkey lengths depend on the axes aspect
    # ratio, and that with angles='xy' their angles also depend on the axes
    # aspect ratio.
    X = np.arange(8)
    Y = np.zeros(8)
    angles = X * (np.pi / 4)
    uv = np.exp(1j * angles)
    U = uv.real
    V = uv.imag
    fig, axs = plt.subplots(2)
    for ax, angle_str in zip(axs, ('uv', 'xy')):
        ax.set_xlim(-1, 8)
        ax.set_ylim(-0.2, 0.2)
        q = ax.quiver(X, Y, U, V, pivot='middle',
                      units='xy', width=0.05,
                      scale=2, scale_units='xy',
                      angles=angle_str)
        for x, angle in zip((0.2, 0.5, 0.8), (0, 45, 90)):
            ax.quiverkey(q, X=x, Y=0.8, U=1, angle=angle, label='', color='b')


@image_comparison(['barbs_test_image.png'], remove_text=True)
def test_barbs():
    """
    Generate a barb plot with customizable properties.
    
    This function creates a barb plot using the given vector components U and V.
    The plot can be customized with various parameters such as the size of empty
    barbs, spacing, and height. Additionally, a colormap can be applied to the
    plot.
    
    Parameters:
    x (array-like): 1D array of x coordinates.
    U (array-like): 2D array of u components of the vector field.
    V (array-like):
    """

    x = np.linspace(-5, 5, 5)
    X, Y = np.meshgrid(x, x)
    U, V = 12*X, 12*Y
    fig, ax = plt.subplots()
    ax.barbs(X, Y, U, V, np.hypot(U, V), fill_empty=True, rounding=False,
             sizes=dict(emptybarb=0.25, spacing=0.2, height=0.3),
             cmap='viridis')


@image_comparison(['barbs_pivot_test_image.png'], remove_text=True)
def test_barbs_pivot():
    x = np.linspace(-5, 5, 5)
    X, Y = np.meshgrid(x, x)
    U, V = 12*X, 12*Y
    fig, ax = plt.subplots()
    ax.barbs(X, Y, U, V, fill_empty=True, rounding=False, pivot=1.7,
             sizes=dict(emptybarb=0.25, spacing=0.2, height=0.3))
    ax.scatter(X, Y, s=49, c='black')


@image_comparison(['barbs_test_flip.png'], remove_text=True)
def test_barbs_flip():
    """Test barbs with an array for flip_barb."""
    x = np.linspace(-5, 5, 5)
    X, Y = np.meshgrid(x, x)
    U, V = 12*X, 12*Y
    fig, ax = plt.subplots()
    ax.barbs(X, Y, U, V, fill_empty=True, rounding=False, pivot=1.7,
             sizes=dict(emptybarb=0.25, spacing=0.2, height=0.3),
             flip_barb=Y < 0)


def test_barb_copy():
    fig, ax = plt.subplots()
    u = np.array([1.1])
    v = np.array([2.2])
    b0 = ax.barbs([1], [1], u, v)
    u[0] = 0
    assert b0.u[0] == 1.1
    v[0] = 0
    assert b0.v[0] == 2.2


def test_bad_masked_sizes():
    """Test error handling when given differing sized masked arrays."""
    x = np.arange(3)
    y = np.arange(3)
    u = np.ma.array(15. * np.ones((4,)))
    v = np.ma.array(15. * np.ones_like(u))
    u[1] = np.ma.masked
    v[1] = np.ma.masked
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        ax.barbs(x, y, u, v)


def test_angles_and_scale():
    """
    Create a quiver plot with specified angles and scale units.
    
    This function generates a quiver plot using the provided grid of X and Y coordinates. Each vector's direction is determined by the angles array, and the scale of the vectors is adjusted based on the scale_units keyword argument.
    
    Parameters:
    X (array-like): 2D array of x coordinates.
    Y (array-like): 2D array of y coordinates.
    U (array-like): 2D array of u components of
    """

    # angles array + scale_units kwarg
    fig, ax = plt.subplots()
    X, Y = np.meshgrid(np.arange(15), np.arange(10))
    U = V = np.ones_like(X)
    phi = (np.random.rand(15, 10) - .5) * 150
    ax.quiver(X, Y, U, V, angles=phi, scale_units='xy')


@image_comparison(['quiver_xy.png'], remove_text=True)
def test_quiver_xy():
    # simple arrow pointing from SW to NE
    fig, ax = plt.subplots(subplot_kw=dict(aspect='equal'))
    ax.quiver(0, 0, 1, 1, angles='xy', scale_units='xy', scale=1)
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.1)
    ax.grid()


def test_quiverkey_angles():
    # Check that only a single arrow is plotted for a quiverkey when an array
    # of angles is given to the original quiver plot
    fig, ax = plt.subplots()

    X, Y = np.meshgrid(np.arange(2), np.arange(2))
    U = V = angles = np.ones_like(X)

    q = ax.quiver(X, Y, U, V, angles=angles)
    qk = ax.quiverkey(q, 1, 1, 2, 'Label')
    # The arrows are only created when the key is drawn
    fig.canvas.draw()
    assert len(qk.verts) == 1


def test_quiver_setuvc_numbers():
    """Check that it is possible to set all arrow UVC to the same numbers"""

    fig, ax = plt.subplots()

    X, Y = np.meshgrid(np.arange(2), np.arange(2))
    U = V = np.ones_like(X)

    q = ax.quiver(X, Y, U, V)
    q.set_UVC(0, 1)
