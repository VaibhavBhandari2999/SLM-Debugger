from collections.abc import Iterable, Sequence
from contextlib import ExitStack
import functools
import inspect
import itertools
import logging
from numbers import Real
from operator import attrgetter
import types

import numpy as np

import matplotlib as mpl
from matplotlib import _api, cbook, _docstring, offsetbox
import matplotlib.artist as martist
import matplotlib.axis as maxis
from matplotlib.cbook import _OrderedSet, _check_1d, index_of
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
import matplotlib.font_manager as font_manager
from matplotlib.gridspec import SubplotSpec
import matplotlib.image as mimage
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.rcsetup import cycler, validate_axisbelow
import matplotlib.spines as mspines
import matplotlib.table as mtable
import matplotlib.text as mtext
import matplotlib.ticker as mticker
import matplotlib.transforms as mtransforms

_log = logging.getLogger(__name__)


class _axis_method_wrapper:
    """
    Helper to generate Axes methods wrapping Axis methods.

    After ::

        get_foo = _axis_method_wrapper("xaxis", "get_bar")

    (in the body of a class) ``get_foo`` is a method that forwards it arguments
    to the ``get_bar`` method of the ``xaxis`` attribute, and gets its
    signature and docstring from ``Axis.get_bar``.

    The docstring of ``get_foo`` is built by replacing "this Axis" by "the
    {attr_name}" (i.e., "the xaxis", "the yaxis") in the wrapped method's
    dedented docstring; additional replacements can be given in *doc_sub*.
    """

    def __init__(self, attr_name, method_name, *, doc_sub=None):
        """
        Initialize a new instance of the class with the specified attribute name and method name.
        
        Args:
        attr_name (str): The name of the attribute associated with the method.
        method_name (str): The name of the method to be associated with the attribute.
        doc_sub (dict, optional): A dictionary of substitutions to be made in the docstring. Defaults to None.
        
        This method sets the attribute name and method name for the instance. It also processes the docstring of the method with the
        """

        self.attr_name = attr_name
        self.method_name = method_name
        # Immediately put the docstring in ``self.__doc__`` so that docstring
        # manipulations within the class body work as expected.
        doc = inspect.getdoc(getattr(maxis.Axis, method_name))
        self._missing_subs = []
        if doc:
            doc_sub = {"this Axis": f"the {self.attr_name}", **(doc_sub or {})}
            for k, v in doc_sub.items():
                if k not in doc:  # Delay raising error until we know qualname.
                    self._missing_subs.append(k)
                doc = doc.replace(k, v)
        self.__doc__ = doc

    def __set_name__(self, owner, name):
        # This is called at the end of the class body as
        # ``self.__set_name__(cls, name_under_which_self_is_assigned)``; we
        # rely on that to give the wrapper the correct __name__/__qualname__.
        get_method = attrgetter(f"{self.attr_name}.{self.method_name}")

        def wrapper(self, *args, **kwargs):
            return get_method(self)(*args, **kwargs)

        wrapper.__module__ = owner.__module__
        wrapper.__name__ = name
        wrapper.__qualname__ = f"{owner.__qualname__}.{name}"
        wrapper.__doc__ = self.__doc__
        # Manually copy the signature instead of using functools.wraps because
        # displaying the Axis method source when asking for the Axes method
        # source would be confusing.
        wrapper.__signature__ = inspect.signature(
            getattr(maxis.Axis, self.method_name))

        if self._missing_subs:
            raise ValueError(
                "The definition of {} expected that the docstring of Axis.{} "
                "contains {!r} as substrings".format(
                    wrapper.__qualname__, self.method_name,
                    ", ".join(map(repr, self._missing_subs))))

        setattr(owner, name, wrapper)


class _TransformedBoundsLocator:
    """
    Axes locator for `.Axes.inset_axes` and similarly positioned Axes.

    The locator is a callable object used in `.Axes.set_aspect` to compute the
    Axes location depending on the renderer.
    """

    def __init__(self, bounds, transform):
        """
        *bounds* (a ``[l, b, w, h]`` rectangle) and *transform* together
        specify the position of the inset Axes.
        """
        self._bounds = bounds
        self._transform = transform

    def __call__(self, ax, renderer):
        """
        Generates a transformed bounding box for a given axes object.
        
        This function is called to create a transformed bounding box for a specified axes object within a figure. The bounding box is initially defined by the `_bounds` attribute and is then transformed using the `_transform` attribute, adjusted by subtracting the `transSubfigure` transformation from the figure.
        
        Parameters:
        ax (matplotlib.axes.Axes): The axes object for which the bounding box is being generated.
        renderer (matplotlib.transforms.Transform): The renderer
        """

        # Subtracting transSubfigure will typically rely on inverted(),
        # freezing the transform; thus, this needs to be delayed until draw
        # time as transSubfigure may otherwise change after this is evaluated.
        return mtransforms.TransformedBbox(
            mtransforms.Bbox.from_bounds(*self._bounds),
            self._transform - ax.figure.transSubfigure)


def _process_plot_format(fmt, *, ambiguous_fmt_datakey=False):
    """
    Convert a MATLAB style color/line style format string to a (*linestyle*,
    *marker*, *color*) tuple.

    Example format strings include:

    * 'ko': black circles
    * '.b': blue dots
    * 'r--': red dashed lines
    * 'C2--': the third color in the color cycle, dashed lines

    The format is absolute in the sense that if a linestyle or marker is not
    defined in *fmt*, there is no line or marker. This is expressed by
    returning 'None' for the respective quantity.

    See Also
    --------
    matplotlib.Line2D.lineStyles, matplotlib.colors.cnames
        All possible styles and color format strings.
    """

    linestyle = None
    marker = None
    color = None

    # Is fmt just a colorspec?
    try:
        color = mcolors.to_rgba(fmt)

        # We need to differentiate grayscale '1.0' from tri_down marker '1'
        try:
            fmtint = str(int(fmt))
        except ValueError:
            return linestyle, marker, color  # Yes
        else:
            if fmt != fmtint:
                # user definitely doesn't want tri_down marker
                return linestyle, marker, color  # Yes
            else:
                # ignore converted color
                color = None
    except ValueError:
        pass  # No, not just a color.

    errfmt = ("{!r} is neither a data key nor a valid format string ({})"
              if ambiguous_fmt_datakey else
              "{!r} is not a valid format string ({})")

    i = 0
    while i < len(fmt):
        c = fmt[i]
        if fmt[i:i+2] in mlines.lineStyles:  # First, the two-char styles.
            if linestyle is not None:
                raise ValueError(errfmt.format(fmt, "two linestyle symbols"))
            linestyle = fmt[i:i+2]
            i += 2
        elif c in mlines.lineStyles:
            if linestyle is not None:
                raise ValueError(errfmt.format(fmt, "two linestyle symbols"))
            linestyle = c
            i += 1
        elif c in mlines.lineMarkers:
            if marker is not None:
                raise ValueError(errfmt.format(fmt, "two marker symbols"))
            marker = c
            i += 1
        elif c in mcolors.get_named_colors_mapping():
            if color is not None:
                raise ValueError(errfmt.format(fmt, "two color symbols"))
            color = c
            i += 1
        elif c == 'C' and i < len(fmt) - 1:
            color_cycle_number = int(fmt[i + 1])
            color = mcolors.to_rgba(f"C{color_cycle_number}")
            i += 2
        else:
            raise ValueError(
                errfmt.format(fmt, f"unrecognized character {c!r}"))

    if linestyle is None and marker is None:
        linestyle = mpl.rcParams['lines.linestyle']
    if linestyle is None:
        linestyle = 'None'
    if marker is None:
        marker = 'None'

    return linestyle, marker, color


class _process_plot_var_args:
    """
    Process variable length arguments to `~.Axes.plot`, to support ::

      plot(t, s)
      plot(t1, s1, t2, s2)
      plot(t1, s1, 'ko', t2, s2)
      plot(t1, s1, 'ko', t2, s2, 'r--', t3, e3)

    an arbitrary number of *x*, *y*, *fmt* are allowed
    """
    def __init__(self, axes, command='plot'):
        """
        Initialize a PlotCommand object.
        
        This method sets up a PlotCommand object with the specified axes and plotting command.
        
        Parameters:
        axes (matplotlib.axes.Axes): The axes object to which the plotting command will be applied.
        command (str, optional): The plotting command to use ('plot' by default).
        
        Keyword Arguments:
        None
        
        Returns:
        None: This method does not return any value. It initializes the PlotCommand object.
        
        Example:
        >>> from matplotlib.axes import Axes
        >>>
        """

        self.axes = axes
        self.command = command
        self.set_prop_cycle(None)

    def __getstate__(self):
        # note: it is not possible to pickle a generator (and thus a cycler).
        return {'axes': self.axes, 'command': self.command}

    def __setstate__(self, state):
        self.__dict__ = state.copy()
        self.set_prop_cycle(None)

    def set_prop_cycle(self, cycler):
        if cycler is None:
            cycler = mpl.rcParams['axes.prop_cycle']
        self.prop_cycler = itertools.cycle(cycler)
        self._prop_keys = cycler.keys  # This should make a copy

    def __call__(self, *args, data=None, **kwargs):
        self.axes._process_unit_info(kwargs=kwargs)

        for pos_only in "xy":
            if pos_only in kwargs:
                raise _api.kwarg_error(self.command, pos_only)

        if not args:
            return

        if data is None:  # Process dict views
            args = [cbook.sanitize_sequence(a) for a in args]
        else:  # Process the 'data' kwarg.
            replaced = [mpl._replacer(data, arg) for arg in args]
            if len(args) == 1:
                label_namer_idx = 0
            elif len(args) == 2:  # Can be x, y or y, c.
                # Figure out what the second argument is.
                # 1) If the second argument cannot be a format shorthand, the
                #    second argument is the label_namer.
                # 2) Otherwise (it could have been a format shorthand),
                #    a) if we did perform a substitution, emit a warning, and
                #       use it as label_namer.
                #    b) otherwise, it is indeed a format shorthand; use the
                #       first argument as label_namer.
                try:
                    _process_plot_format(args[1])
                except ValueError:  # case 1)
                    label_namer_idx = 1
                else:
                    if replaced[1] is not args[1]:  # case 2a)
                        _api.warn_external(
                            f"Second argument {args[1]!r} is ambiguous: could "
                            f"be a format string but is in 'data'; using as "
                            f"data.  If it was intended as data, set the "
                            f"format string to an empty string to suppress "
                            f"this warning.  If it was intended as a format "
                            f"string, explicitly pass the x-values as well.  "
                            f"Alternatively, rename the entry in 'data'.",
                            RuntimeWarning)
                        label_namer_idx = 1
                    else:  # case 2b)
                        label_namer_idx = 0
            elif len(args) == 3:
                label_namer_idx = 1
            else:
                raise ValueError(
                    "Using arbitrary long args with data is not supported due "
                    "to ambiguity of arguments; use multiple plotting calls "
                    "instead")
            if kwargs.get("label") is None:
                kwargs["label"] = mpl._label_from_arg(
                    replaced[label_namer_idx], args[label_namer_idx])
            args = replaced
        ambiguous_fmt_datakey = data is not None and len(args) == 2

        if len(args) >= 4 and not cbook.is_scalar_or_string(
                kwargs.get("label")):
            raise ValueError("plot() with multiple groups of data (i.e., "
                             "pairs of x and y) does not support multiple "
                             "labels")

        # Repeatedly grab (x, y) or (x, y, format) from the front of args and
        # massage them into arguments to plot() or fill().

        while args:
            this, args = args[:2], args[2:]
            if args and isinstance(args[0], str):
                this += args[0],
                args = args[1:]
            yield from se
