import matplotlib.axes as maxes
from matplotlib.artist import Artist
from matplotlib.axis import XAxis, YAxis


class SimpleChainedObjects:
    def __init__(self, objects):
        self._objects = objects

    def __getattr__(self, k):
        _a = SimpleChainedObjects([getattr(a, k) for a in self._objects])
        return _a

    def __call__(self, *args, **kwargs):
        for m in self._objects:
            m(*args, **kwargs)


class Axes(maxes.Axes):

    class AxisDict(dict):
        def __init__(self, axes):
            self.axes = axes
            super().__init__()

        def __getitem__(self, k):
            """
            Retrieve an item from the Axes.AxisDict.
            
            This method allows retrieval of items based on a key or a slice. If the key is a tuple, it retrieves multiple items using `super().__getitem__` and returns them as a `SimpleChainedObjects` instance. If the key is a slice, it checks if the slice is empty (i.e., no start, stop, or step specified) and returns all values as a `SimpleChainedObjects` instance. Otherwise, it raises
            """

            if isinstance(k, tuple):
                r = SimpleChainedObjects(
                    # super() within a list comprehension needs explicit args.
                    [super(Axes.AxisDict, self).__getitem__(k1) for k1 in k])
                return r
            elif isinstance(k, slice):
                if k.start is None and k.stop is None and k.step is None:
                    return SimpleChainedObjects(list(self.values()))
                else:
                    raise ValueError("Unsupported slice")
            else:
                return dict.__getitem__(self, k)

        def __call__(self, *v, **kwargs):
            return maxes.Axes.axis(self.axes, *v, **kwargs)

    @property
    def axis(self):
        return self._axislines

    def clear(self):
        """
        Clears the axes by removing all lines, text, images, etc.
        
        This method clears the axes by removing all lines, text, images, and other
        graphical elements. It also reinitializes the axis artists.
        
        Parameters:
        None
        
        Returns:
        None
        
        Methods Invoked:
        - `super().clear()`: Clears the parent object's contents.
        - `self._axislines`: Initializes and updates the axis artists.
        - `self.AxisDict(self
        """

        # docstring inherited
        super().clear()
        # Init axis artists.
        self._axislines = self.AxisDict(self)
        self._axislines.update(
            bottom=SimpleAxisArtist(self.xaxis, 1, self.spines["bottom"]),
            top=SimpleAxisArtist(self.xaxis, 2, self.spines["top"]),
            left=SimpleAxisArtist(self.yaxis, 1, self.spines["left"]),
            right=SimpleAxisArtist(self.yaxis, 2, self.spines["right"]))


class SimpleAxisArtist(Artist):
    def __init__(self, axis, axisnum, spine):
        """
        Initialize a new Spine object.
        
        Args:
        axis (XAxis or YAxis): The axis associated with this spine.
        axisnum (int): The number of the axis (1 or 2).
        spine (Line2D): The spine line representing the axis.
        
        Attributes:
        _axis (XAxis or YAxis): The axis associated with this spine.
        _axisnum (int): The number of the axis (1 or 2).
        line (Line2
        """

        self._axis = axis
        self._axisnum = axisnum
        self.line = spine

        if isinstance(axis, XAxis):
            self._axis_direction = ["bottom", "top"][axisnum-1]
        elif isinstance(axis, YAxis):
            self._axis_direction = ["left", "right"][axisnum-1]
        else:
            raise ValueError(
                f"axis must be instance of XAxis or YAxis, but got {axis}")
        super().__init__()

    @property
    def major_ticks(self):
        """
        Generates major tick lines for an axis.
        
        This function retrieves major tick lines from the specified axis using the `get_major_ticks` method. It then creates a list of tick lines by accessing the corresponding attribute (e.g., `tick1line`, `tick2line`) for each major tick object.
        
        Args:
        None
        
        Returns:
        A SimpleChainedObjects instance containing the major tick lines for the axis.
        """

        tickline = "tick%dline" % self._axisnum
        return SimpleChainedObjects([getattr(tick, tickline)
                                     for tick in self._axis.get_major_ticks()])

    @property
    def major_ticklabels(self):
        """
        Generates major tick labels for an axis.
        
        This function retrieves major tick labels from the specified axis using
        the `get_major_ticks` method. It then accesses the attribute named
        'label%d' (where %d is the axis number) of each tick object and returns
        them as a list of SimpleChainedObjects.
        
        Args:
        None
        
        Returns:
        A list of SimpleChainedObjects representing the major tick labels.
        """

        label = "label%d" % self._axisnum
        return SimpleChainedObjects([getattr(tick, label)
                                     for tick in self._axis.get_major_ticks()])

    @property
    def label(self):
        return self._axis.label

    def set_visible(self, b):
        """
        Sets the visibility of the plot elements.
        
        Parameters:
        -----------
        b : bool
        A boolean value indicating whether the plot elements should be visible (True) or not (False).
        
        This method toggles the visibility of the plot elements by setting the visibility of the line and axis based on the input boolean value `b`. It also calls the `toggle` method with the argument `all=b` and the `set_visible` method of the superclass with the same argument.
        """

        self.toggle(all=b)
        self.line.set_visible(b)
        self._axis.set_visible(True)
        super().set_visible(b)

    def set_label(self, txt):
        self._axis.set_label_text(txt)

    def toggle(self, all=None, ticks=None, ticklabels=None, label=None):
        """
        Toggles visibility of axis ticks, tick labels, and axis label.
        
        This method controls the visibility of ticks, tick labels, and the axis label on a specified axis. It accepts parameters to enable or disable these elements individually or collectively.
        
        Parameters:
        all (bool, optional): If `True`, all elements (ticks, tick labels, and label) are toggled to their opposite state. If `False`, all elements remain unchanged.
        ticks (bool, optional): If `True
        """


        if all:
            _ticks, _ticklabels, _label = True, True, True
        elif all is not None:
            _ticks, _ticklabels, _label = False, False, False
        else:
            _ticks, _ticklabels, _label = None, None, None

        if ticks is not None:
            _ticks = ticks
        if ticklabels is not None:
            _ticklabels = ticklabels
        if label is not None:
            _label = label

        if _ticks is not None:
            tickparam = {f"tick{self._axisnum}On": _ticks}
            self._axis.set_tick_params(**tickparam)
        if _ticklabels is not None:
            tickparam = {f"label{self._axisnum}On": _ticklabels}
            self._axis.set_tick_params(**tickparam)

        if _label is not None:
            pos = self._axis.get_label_position()
            if (pos == self._axis_direction) and not _label:
                self._axis.label.set_visible(False)
            elif _label:
                self._axis.label.set_visible(True)
                self._axis.set_label_position(self._axis_direction)
