from datetime import datetime, timezone, timedelta
import platform
from unittest.mock import MagicMock

import matplotlib.pyplot as plt
from matplotlib.testing.decorators import check_figures_equal, image_comparison
import matplotlib.units as munits
from matplotlib.category import UnitData
import numpy as np
import pytest


# Basic class that wraps numpy array and has units
class Quantity:
    def __init__(self, data, units):
        self.magnitude = data
        self.units = units

    def to(self, new_units):
        factors = {('hours', 'seconds'): 3600, ('minutes', 'hours'): 1 / 60,
                   ('minutes', 'seconds'): 60, ('feet', 'miles'): 1 / 5280.,
                   ('feet', 'inches'): 12, ('miles', 'inches'): 12 * 5280}
        if self.units != new_units:
            mult = factors[self.units, new_units]
            return Quantity(mult * self.magnitude, new_units)
        else:
            return Quantity(self.magnitude, self.units)

    def __copy__(self):
        return Quantity(self.magnitude, self.units)

    def __getattr__(self, attr):
        return getattr(self.magnitude, attr)

    def __getitem__(self, item):
        """
        Retrieve the item from the Quantity object.
        
        Parameters:
        item (int, slice, or array-like): The index or slice to retrieve from the magnitude array.
        
        Returns:
        Quantity: A new Quantity object with the selected item as the magnitude and the same units.
        
        Notes:
        - If the magnitude is an iterable, the function returns a new Quantity object with the selected item as the magnitude.
        - If the magnitude is not iterable, the function returns a new Quantity object with the entire magnitude and
        """

        if np.iterable(self.magnitude):
            return Quantity(self.magnitude[item], self.units)
        else:
            return Quantity(self.magnitude, self.units)

    def __array__(self):
        return np.asarray(self.magnitude)


@pytest.fixture
def quantity_converter():
    """
    Function to create a quantity converter interface for unit conversion and axis information.
    
    This function sets up a mock conversion interface that can be used to convert quantities to specified units and retrieve default units for a given axis. The interface also provides axis information, such as the label and default limits.
    
    Parameters:
    None
    
    Returns:
    qc (unittest.mock.MagicMock): A mock object representing the conversion interface with the following methods:
    - convert(value, unit, axis): Converts a value or iterable of values to
    """

    # Create an instance of the conversion interface and
    # mock so we can check methods called
    qc = munits.ConversionInterface()

    def convert(value, unit, axis):
        if hasattr(value, 'units'):
            return value.to(unit).magnitude
        elif np.iterable(value):
            try:
                return [v.to(unit).magnitude for v in value]
            except AttributeError:
                return [Quantity(v, axis.get_units()).to(unit).magnitude
                        for v in value]
        else:
            return Quantity(value, axis.get_units()).to(unit).magnitude

    def default_units(value, axis):
        if hasattr(value, 'units'):
            return value.units
        elif np.iterable(value):
            for v in value:
                if hasattr(v, 'units'):
                    return v.units
            return None

    qc.convert = MagicMock(side_effect=convert)
    qc.axisinfo = MagicMock(side_effect=lambda u, a:
                            munits.AxisInfo(label=u, default_limits=(0, 100)))
    qc.default_units = MagicMock(side_effect=default_units)
    return qc


# Tests that the conversion machinery works properly for classes that
# work as a facade over numpy arrays (like pint)
@image_comparison(['plot_pint.png'], style='mpl20',
                  tol=0 if platform.machine() == 'x86_64' else 0.01)
def test_numpy_facade(quantity_converter):
    # use former defaults to match existing baseline image
    plt.rcParams['axes.formatter.limits'] = -7, 7

    # Register the class
    munits.registry[Quantity] = quantity_converter

    # Simple test
    y = Quantity(np.linspace(0, 30), 'miles')
    x = Quantity(np.linspace(0, 5), 'hours')

    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.15)  # Make space for label
    ax.plot(x, y, 'tab:blue')
    ax.axhline(Quantity(26400, 'feet'), color='tab:red')
    ax.axvline(Quantity(120, 'minutes'), color='tab:green')
    ax.yaxis.set_units('inches')
    ax.xaxis.set_units('seconds')

    assert quantity_converter.convert.called
    assert quantity_converter.axisinfo.called
    assert quantity_converter.default_units.called


# Tests gh-8908
@image_comparison(['plot_masked_units.png'], remove_text=True, style='mpl20',
                  tol=0 if platform.machine() == 'x86_64' else 0.01)
def test_plot_masked_units():
    """
    Plot masked units data.
    
    This function creates a plot of masked units data on a given axis.
    
    Parameters:
    data (numpy.ndarray): The array of data points to be plotted.
    
    Returns:
    matplotlib.figure.Figure: The figure object containing the plot.
    matplotlib.axes.Axes: The axes object containing the plot.
    
    Example:
    >>> data = np.linspace(-5, 5)
    >>> data_masked = np.ma.array(data, mask=(data > -2) & (data <
    """

    data = np.linspace(-5, 5)
    data_masked = np.ma.array(data, mask=(data > -2) & (data < 2))
    data_masked_units = Quantity(data_masked, 'meters')

    fig, ax = plt.subplots()
    ax.plot(data_masked_units)


def test_empty_set_limits_with_units(quantity_converter):
    # Register the class
    munits.registry[Quantity] = quantity_converter

    fig, ax = plt.subplots()
    ax.set_xlim(Quantity(-1, 'meters'), Quantity(6, 'meters'))
    ax.set_ylim(Quantity(-1, 'hours'), Quantity(16, 'hours'))


@image_comparison(['jpl_bar_units.png'],
                  savefig_kwarg={'dpi': 120}, style='mpl20')
def test_jpl_bar_units():
    """
    Test the bar function with JPL units.
    
    This function tests the bar function from matplotlib with JPL units. It registers the units, defines a duration for a day, creates a list of x-values and their corresponding weights, and sets a baseline epoch. It then creates a bar plot and sets the y-axis limits based on the baseline epoch and the weights.
    
    Parameters:
    None
    
    Returns:
    None
    """

    import matplotlib.testing.jpl_units as units
    units.register()

    day = units.Duration("ET", 24.0 * 60.0 * 60.0)
    x = [0 * units.km, 1 * units.km, 2 * units.km]
    w = [1 * day, 2 * day, 3 * day]
    b = units.Epoch("ET", dt=datetime(2009, 4, 25))
    fig, ax = plt.subplots()
    ax.bar(x, w, bottom=b)
    ax.set_ylim([b - 1 * day, b + w[-1] + (1.001) * day])


@image_comparison(['jpl_barh_units.png'],
                  savefig_kwarg={'dpi': 120}, style='mpl20')
def test_jpl_barh_units():
    import matplotlib.testing.jpl_units as units
    units.register()

    day = units.Duration("ET", 24.0 * 60.0 * 60.0)
    x = [0 * units.km, 1 * units.km, 2 * units.km]
    w = [1 * day, 2 * day, 3 * day]
    b = units.Epoch("ET", dt=datetime(2009, 4, 25))

    fig, ax = plt.subplots()
    ax.barh(x, w, left=b)
    ax.set_xlim([b - 1 * day, b + w[-1] + (1.001) * day])


def test_empty_arrays():
    # Check that plotting an empty array with a dtype works
    plt.scatter(np.array([], dtype='datetime64[ns]'), np.array([]))


def test_scatter_element0_masked():
    """
    Create a scatter plot with masked data.
    
    This function generates a scatter plot using matplotlib for a given set of
    datetime values and corresponding y-values. The first y-value is masked as
    NaN, which should be handled appropriately by the scatter plot.
    
    Parameters:
    None
    
    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the plot.
    ax (matplotlib.axes.Axes): The axes object containing the scatter plot.
    
    Notes:
    - The function uses numpy to create and manipulate the
    """

    times = np.arange('2005-02', '2005-03', dtype='datetime64[D]')
    y = np.arange(len(times), dtype=float)
    y[0] = np.nan
    fig, ax = plt.subplots()
    ax.scatter(times, y)
    fig.canvas.draw()


def test_errorbar_mixed_units():
    x = np.arange(10)
    y = [datetime(2020, 5, i * 2 + 1) for i in x]
    fig, ax = plt.subplots()
    ax.errorbar(x, y, timedelta(days=0.5))
    fig.canvas.draw()


@check_figures_equal(extensions=["png"])
def test_subclass(fig_test, fig_ref):
    class subdate(datetime):
        pass

    fig_test.subplots().plot(subdate(2000, 1, 1), 0, "o")
    fig_ref.subplots().plot(datetime(2000, 1, 1), 0, "o")


def test_shared_axis_quantity(quantity_converter):
    munits.registry[Quantity] = quantity_converter
    x = Quantity(np.linspace(0, 1, 10), "hours")
    y1 = Quantity(np.linspace(1, 2, 10), "feet")
    y2 = Quantity(np.linspace(3, 4, 10), "feet")
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all', sharey='all')
    ax1.plot(x, y1)
    ax2.plot(x, y2)
    assert ax1.xaxis.get_units() == ax2.xaxis.get_units() == "hours"
    assert ax2.yaxis.get_units() == ax2.yaxis.get_units() == "feet"
    ax1.xaxis.set_units("seconds")
    ax2.yaxis.set_units("inches")
    assert ax1.xaxis.get_units() == ax2.xaxis.get_units() == "seconds"
    assert ax1.yaxis.get_units() == ax2.yaxis.get_units() == "inches"


def test_shared_axis_datetime():
    # datetime uses dates.DateConverter
    y1 = [datetime(2020, i, 1, tzinfo=timezone.utc) for i in range(1, 13)]
    y2 = [datetime(2021, i, 1, tzinfo=timezone.utc) for i in range(1, 13)]
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    ax1.plot(y1)
    ax2.plot(y2)
    ax1.yaxis.set_units(timezone(timedelta(hours=5)))
    assert ax2.yaxis.units == timezone(timedelta(hours=5))


def test_shared_axis_categorical():
    """
    Plot two categorical data sets on shared axes.
    
    This function creates a figure with two subplots that share the same x and y axes.
    It plots two dictionaries of categorical data on these subplots and sets the x-axis
    units to a custom category. The function ensures that the x-axis units are consistent
    across both subplots.
    
    Parameters:
    None
    
    Returns:
    fig, (ax1, ax2) : tuple
    A tuple containing the figure and the two subplots.
    """

    # str uses category.StrCategoryConverter
    d1 = {"a": 1, "b": 2}
    d2 = {"a": 3, "b": 4}
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)
    ax1.plot(d1.keys(), d1.values())
    ax2.plot(d2.keys(), d2.values())
    ax1.xaxis.set_units(UnitData(["c", "d"]))
    assert "c" in ax2.xaxis.get_units()._mapping.keys()


def test_empty_default_limits(quantity_converter):
    munits.registry[Quantity] = quantity_converter
    fig, ax1 = plt.subplots()
    ax1.xaxis.update_units(Quantity([10], "miles"))
    fig.draw_without_rendering()
    assert ax1.get_xlim() == (0, 100)
    ax1.yaxis.update_units(Quantity([10], "miles"))
    fig.draw_without_rendering()
    assert ax1.get_ylim() == (0, 100)

    fig, ax = plt.subplots()
    ax.axhline(30)
    ax.plot(Quantity(np.arange(0, 3), "miles"),
            Quantity(np.arange(0, 6, 2), "feet"))
    fig.draw_without_rendering()
    assert ax.get_xlim() == (0, 2)
    assert ax.get_ylim() == (0, 30)

    fig, ax = plt.subplots()
    ax.axvline(30)
    ax.plot(Quantity(np.arange(0, 3), "miles"),
            Quantity(np.arange(0, 6, 2), "feet"))
    fig.draw_without_rendering()
    assert ax.get_xlim() == (0, 30)
    assert ax.get_ylim() == (0, 4)

    fig, ax = plt.subplots()
    ax.xaxis.update_units(Quantity([10], "miles"))
    ax.axhline(30)
    fig.draw_without_rendering()
    assert ax.get_xlim() == (0, 100)
    assert ax.get_ylim() == (28.5, 31.5)

    fig, ax = plt.subplots()
    ax.yaxis.update_units(Quantity([10], "miles"))
    ax.axvline(30)
    fig.draw_without_rendering()
    assert ax.get_ylim() == (0, 100)
    assert ax.get_xlim() == (28.5, 31.5)


# test array-like objects...
class Kernel:
    def __init__(self, array):
        self._array = np.asanyarray(array)

    def __array__(self):
        return self._array

    @property
    def shape(self):
        return self._array.shape


def test_plot_kernel():
    # just a smoketest that fail
    kernel = Kernel([1, 2, 3, 4, 5])
    plt.plot(kernel)
