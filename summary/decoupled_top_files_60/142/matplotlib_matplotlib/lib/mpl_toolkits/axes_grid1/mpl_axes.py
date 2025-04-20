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
            Retrieve an item from the Axes.AxisDict object.
            
            Parameters:
            k (tuple or slice or int): The key used to retrieve the item. If `k` is a tuple, it is used to retrieve multiple items. If `k` is a slice, it is used to retrieve a range of items, but only full slices (start, stop, and step all None) are supported.
            
            Returns:
            SimpleChainedObjects: If `k` is a tuple, returns a collection of
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
        Clears the axes and resets the axis artists.
        
        This method clears the axes and resets the axis artists for the current plot. It inherits the behavior from the superclass and then initializes the axis artists for the bottom, top, left, and right spines.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        _axislines (dict): A dictionary containing the axis artists for the bottom, top, left, and right spines.
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
        Initialize a Spine object.
        
        This method initializes a Spine object, which is associated with a specific axis and spine on a plot.
        
        Parameters:
        axis (XAxis or YAxis): The axis object to which the spine belongs.
        axisnum (int): The number indicating the position of the axis (1 or 2).
        spine (matplotlib.spines.Spine): The spine object representing the edge of the plot area.
        
        Returns:
        None: This method does not return any value.
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
        tickline = "tick%dline" % self._axisnum
        return SimpleChainedObjects([getattr(tick, tickline)
                                     for tick in self._axis.get_major_ticks()])

    @property
    def major_ticklabels(self):
        """
        Generates the major tick labels for a given axis.
        
        This function retrieves the major tick labels for a specified axis. Each tick on the axis has a corresponding label, and this function collects these labels into a list.
        
        Parameters:
        None (the function is a method of a class and thus operates on the instance's attributes)
        
        Returns:
        list: A list of the major tick labels for the axis.
        
        Notes:
        - The labels are accessed through the `SimpleChainedObjects` class, which
        """

        label = "label%d" % self._axisnum
        return SimpleChainedObjects([getattr(tick, label)
                                     for tick in self._axis.get_major_ticks()])

    @property
    def label(self):
        return self._axis.label

    def set_visible(self, b):
        self.toggle(all=b)
        self.line.set_visible(b)
        self._axis.set_visible(True)
        super().set_visible(b)

    def set_label(self, txt):
        self._axis.set_label_text(txt)

    def toggle(self, all=None, ticks=None, ticklabels=None, label=None):

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
