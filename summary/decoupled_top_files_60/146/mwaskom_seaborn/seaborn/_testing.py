import numpy as np
import matplotlib as mpl
from matplotlib.colors import to_rgb, to_rgba
from numpy.testing import assert_array_equal


USE_PROPS = [
    "alpha",
    "edgecolor",
    "facecolor",
    "fill",
    "hatch",
    "height",
    "linestyle",
    "linewidth",
    "paths",
    "xy",
    "xydata",
    "sizes",
    "zorder",
]


def assert_artists_equal(list1, list2):
    """
    Asserts that two lists of artists are equal.
    
    Parameters:
    list1 (list): The first list of artists to compare.
    list2 (list): The second list of artists to compare.
    
    This function checks that the two provided lists of artists are equal in length and that each corresponding artist in the lists are of the same class. It then compares the properties of each artist, ensuring that specific properties such as 'paths', 'color', and others are equal. For 'paths', it compares
    """


    assert len(list1) == len(list2)
    for a1, a2 in zip(list1, list2):
        assert a1.__class__ == a2.__class__
        prop1 = a1.properties()
        prop2 = a2.properties()
        for key in USE_PROPS:
            if key not in prop1:
                continue
            v1 = prop1[key]
            v2 = prop2[key]
            if key == "paths":
                for p1, p2 in zip(v1, v2):
                    assert_array_equal(p1.vertices, p2.vertices)
                    assert_array_equal(p1.codes, p2.codes)
            elif key == "color":
                v1 = mpl.colors.to_rgba(v1)
                v2 = mpl.colors.to_rgba(v2)
                assert v1 == v2
            elif isinstance(v1, np.ndarray):
                assert_array_equal(v1, v2)
            else:
                assert v1 == v2


def assert_legends_equal(leg1, leg2):
    """
    Assert that two legend objects are equal.
    
    This function checks if two legend objects have the same title and texts, as well as their corresponding artists (lines and patches).
    
    Parameters:
    leg1 (matplotlib.legend.Legend): The first legend object to compare.
    leg2 (matplotlib.legend.Legend): The second legend object to compare.
    
    Returns:
    None: The function raises an AssertionError if the legends are not equal.
    """


    assert leg1.get_title().get_text() == leg2.get_title().get_text()
    for t1, t2 in zip(leg1.get_texts(), leg2.get_texts()):
        assert t1.get_text() == t2.get_text()

    assert_artists_equal(
        leg1.get_patches(), leg2.get_patches(),
    )
    assert_artists_equal(
        leg1.get_lines(), leg2.get_lines(),
    )


def assert_plots_equal(ax1, ax2, labels=True):

    assert_artists_equal(ax1.patches, ax2.patches)
    assert_artists_equal(ax1.lines, ax2.lines)
    assert_artists_equal(ax1.collections, ax2.collections)

    if labels:
        assert ax1.get_xlabel() == ax2.get_xlabel()
        assert ax1.get_ylabel() == ax2.get_ylabel()


def assert_colors_equal(a, b, check_alpha=True):
    """
    Asserts that two color arrays or single colors are equal, considering or ignoring alpha channel.
    
    Parameters:
    a (array-like or tuple): The first color or array of colors to compare.
    b (array-like or tuple): The second color or array of colors to compare.
    check_alpha (bool): If True (default), the alpha channel is included in the comparison. If False, the alpha channel is ignored.
    
    This function compares the given colors or arrays of colors. If `check_alpha
    """


    def handle_array(x):
        """
        Handle an input array to ensure it is a 1-dimensional NumPy array with unique elements.
        
        Parameters:
        x (array-like): Input array or object that can be converted to a NumPy array.
        
        Returns:
        np.ndarray: A 1-dimensional NumPy array with unique elements.
        
        Raises:
        ValueError: If the input array is not 1-dimensional after ensuring it has unique elements.
        
        Notes:
        - If the input is already a 1-dimensional NumPy array, it is returned as
        """


        if isinstance(x, np.ndarray):
            if x.ndim > 1:
                x = np.unique(x, axis=0).squeeze()
            if x.ndim > 1:
                raise ValueError("Color arrays must be 1 dimensional")
        return x

    a = handle_array(a)
    b = handle_array(b)

    f = to_rgba if check_alpha else to_rgb
    assert f(a) == f(b)
