from matplotlib import cbook
from matplotlib.artist import Artist


class Container(tuple):
    """
    Base class for containers.

    Containers are classes that collect semantically related Artists such as
    the bars of a bar plot.
    """

    def __repr__(self):
        return ("<{} object of {} artists>"
                .format(type(self).__name__, len(self)))

    def __new__(cls, *args, **kwargs):
        return tuple.__new__(cls, args[0])

    def __init__(self, kl, label=None):
        """
        Initialize a Line2D object.
        
        Parameters:
        - kl (object): The data to be plotted by the Line2D object.
        - label (str, optional): A label for the line. Defaults to None.
        
        This method sets up a Line2D object with the given data and an optional label. It also initializes a callback registry for the 'pchanged' signal and sets the label for the line. No return value is expected.
        """

        self._callbacks = cbook.CallbackRegistry(signals=["pchanged"])
        self._remove_method = None
        self.set_label(label)

    def remove(self):
        """
        Remove the artist from the figure if it is in the figure.
        
        This function will recursively remove all child artists as well.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        Notes
        -----
        This function is called internally by the framework and is not typically
        called directly by the user. It is used to clean up the figure by removing
        artists that are no longer needed.
        """

        for c in cbook.flatten(
                self, scalarp=lambda x: isinstance(x, Artist)):
            if c is not None:
                c.remove()
        if self._remove_method:
            self._remove_method(self)

    def get_children(self):
        return [child for child in cbook.flatten(self) if child is not None]

    get_label = Artist.get_label
    set_label = Artist.set_label
    add_callback = Artist.add_callback
    remove_callback = Artist.remove_callback
    pchanged = Artist.pchanged


class BarContainer(Container):
    """
    Container for the artists of bar plots (e.g. created by `.Axes.bar`).

    The container can be treated as a tuple of the *patches* themselves.
    Additionally, you can access these and further parameters by the
    attributes.

    Attributes
    ----------
    patches : list of :class:`~matplotlib.patches.Rectangle`
        The artists of the bars.

    errorbar : None or :class:`~matplotlib.container.ErrorbarContainer`
        A container for the error bar artists if error bars are present.
        *None* otherwise.

    datavalues : None or array-like
        The underlying data values corresponding to the bars.

    orientation : {'vertical', 'horizontal'}, default: None
        If 'vertical', the bars are assumed to be vertical.
        If 'horizontal', the bars are assumed to be horizontal.

    """

    def __init__(self, patches, errorbar=None, *, datavalues=None,
        """
        Initialize a BarPlot object.
        
        This method initializes a BarPlot object with the given patches and optional errorbar, datavalues, and orientation. Additional keyword arguments can be provided for further customization.
        
        Parameters:
        patches (list): A list of patches representing the bars.
        errorbar (ErrorbarContainer, optional): An errorbar container object.
        datavalues (array-like, optional): Data values for the bars.
        orientation (str, optional): Orientation of the bars ('vertical'
        """

                 orientation=None, **kwargs):
        self.patches = patches
        self.errorbar = errorbar
        self.datavalues = datavalues
        self.orientation = orientation
        super().__init__(patches, **kwargs)


class ErrorbarContainer(Container):
    """
    Container for the artists of error bars (e.g. created by `.Axes.errorbar`).

    The container can be treated as the *lines* tuple itself.
    Additionally, you can access these and further parameters by the
    attributes.

    Attributes
    ----------
    lines : tuple
        Tuple of ``(data_line, caplines, barlinecols)``.

        - data_line : :class:`~matplotlib.lines.Line2D` instance of
          x, y plot markers and/or line.
        - caplines : tuple of :class:`~matplotlib.lines.Line2D` instances of
          the error bar caps.
        - barlinecols : list of :class:`~matplotlib.collections.LineCollection`
          with the horizontal and vertical error ranges.

    has_xerr, has_yerr : bool
        ``True`` if the errorbar has x/y errors.

    """

    def __init__(self, lines, has_xerr=False, has_yerr=False, **kwargs):
        """
        Initialize a LineCollection object.
        
        Parameters:
        lines (list): A list of line segments to be included in the collection.
        has_xerr (bool, optional): Indicates whether the lines have x error bars. Default is False.
        has_yerr (bool, optional): Indicates whether the lines have y error bars. Default is False.
        **kwargs: Additional keyword arguments to be passed to the superclass.
        
        This method initializes a LineCollection object with the specified lines and error bar indicators. The
        """

        self.lines = lines
        self.has_xerr = has_xerr
        self.has_yerr = has_yerr
        super().__init__(lines, **kwargs)


class StemContainer(Container):
    """
    Container for the artists created in a :meth:`.Axes.stem` plot.

    The container can be treated like a namedtuple ``(markerline, stemlines,
    baseline)``.

    Attributes
    ----------
    markerline :  :class:`~matplotlib.lines.Line2D`
        The artist of the markers at the stem heads.

    stemlines : list of :class:`~matplotlib.lines.Line2D`
        The artists of the vertical lines for all stems.

    baseline : :class:`~matplotlib.lines.Line2D`
        The artist of the horizontal baseline.
    """
    def __init__(self, markerline_stemlines_baseline, **kwargs):
        """
        Parameters
        ----------
        markerline_stemlines_baseline : tuple
            Tuple of ``(markerline, stemlines, baseline)``.
            ``markerline`` contains the `.LineCollection` of the markers,
            ``stemlines`` is a `.LineCollection` of the main lines,
            ``baseline`` is the `.Line2D` of the baseline.
        """
        markerline, stemlines, baseline = markerline_stemlines_baseline
        self.markerline = markerline
        self.stemlines = stemlines
        self.baseline = baseline
        super().__init__(markerline_stemlines_baseline, **kwargs)
