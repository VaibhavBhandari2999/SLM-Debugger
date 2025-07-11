"""
Classes to support contour plotting and labelling for the Axes class.
"""

import functools
import math
from numbers import Integral

import numpy as np
from numpy import ma

import matplotlib as mpl
from matplotlib import _api, _docstring
from matplotlib.backend_bases import MouseButton
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.text import Text
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.collections as mcoll
import matplotlib.font_manager as font_manager
import matplotlib.cbook as cbook
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms


@_api.deprecated("3.7", alternative="Text.set_transform_rotates_text")
class ClabelText(Text):
    """
    Unlike the ordinary text, the get_rotation returns an updated
    angle in the pixel coordinate assuming that the input rotation is
    an angle in data coordinate (or whatever transform set).
    """

    def get_rotation(self):
        new_angle, = self.get_transform().transform_angles(
            [super().get_rotation()], [self.get_position()])
        return new_angle


def _contour_labeler_event_handler(cs, inline, inline_spacing, event):
    canvas = cs.axes.figure.canvas
    is_button = event.name == "button_press_event"
    is_key = event.name == "key_press_event"
    # Quit (even if not in infinite mode; this is consistent with
    # MATLAB and sometimes quite useful, but will require the user to
    # test how many points were actually returned before using data).
    if (is_button and event.button == MouseButton.MIDDLE
            or is_key and event.key in ["escape", "enter"]):
        canvas.stop_event_loop()
    # Pop last click.
    elif (is_button and event.button == MouseButton.RIGHT
          or is_key and event.key in ["backspace", "delete"]):
        # Unfortunately, if one is doing inline labels, then there is currently
        # no way to fix the broken contour - once humpty-dumpty is broken, he
        # can't be put back together.  In inline mode, this does nothing.
        if not inline:
            cs.pop_label()
            canvas.draw()
    # Add new click.
    elif (is_button and event.button == MouseButton.LEFT
          # On macOS/gtk, some keys return None.
          or is_key and event.key is not None):
        if cs.axes.contains(event)[0]:
            cs.add_label_near(event.x, event.y, transform=False,
                              inline=inline, inline_spacing=inline_spacing)
            canvas.draw()


class ContourLabeler:
    """Mixin to provide labelling capability to `.ContourSet`."""

    def clabel(self, levels=None, *,
               fontsize=None, inline=True, inline_spacing=5, fmt=None,
               colors=None, use_clabeltext=False, manual=False,
               rightside_up=True, zorder=None):
        """
        Label a contour plot.

        Adds labels to line contours in this `.ContourSet` (which inherits from
        this mixin class).

        Parameters
        ----------
        levels : array-like, optional
            A list of level values, that should be labeled. The list must be
            a subset of ``cs.levels``. If not given, all levels are labeled.

        fontsize : str or float, default: :rc:`font.size`
            Size in points or relative size e.g., 'smaller', 'x-large'.
            See `.Text.set_size` for accepted string values.

        colors : color or colors or None, default: None
            The label colors:

            - If *None*, the color of each label matches the color of
              the corresponding contour.

            - If one string color, e.g., *colors* = 'r' or *colors* =
              'red', all labels will be plotted in this color.

            - If a tuple of colors (string, float, RGB, etc), different labels
              will be plotted in different colors in the order specified.

        inline : bool, default: True
            If ``True`` the underlying contour is removed where the label is
            placed.

        inline_spacing : float, default: 5
            Space in pixels to leave on each side of label when placing inline.

            This spacing will be exact for labels at locations where the
            contour is straight, less so for labels on curved contours.

        fmt : `.Formatter` or str or callable or dict, optional
            How the levels are formatted:

            - If a `.Formatter`, it is used to format all levels at once, using
              its `.Formatter.format_ticks` method.
            - If a str, it is interpreted as a %-style format string.
            - If a callable, it is called with one level at a time and should
              return the corresponding label.
            - If a dict, it should directly map levels to labels.

            The default is to use a standard `.ScalarFormatter`.

        manual : bool or iterable, default: False
            If ``True``, contour labels will be placed manually using
            mouse clicks. Click the first button near a contour to
            add a label, click the second button (or potentially both
            mouse buttons at once) to finish adding labels. The third
            button can be used to remove the last label added, but
            only if labels are not inline. Alternatively, the keyboard
            can be used to select label locations (enter to end label
            placement, delete or backspace act like the third mouse button,
            and any other key will select a label location).

            *manual* can also be an iterable object of (x, y) tuples.
            Contour labels will be created as if mouse is clicked at each
            (x, y) position.

        rightside_up : bool, default: True
            If ``True``, label rotations will always be plus
            or minus 90 degrees from level.

        use_clabeltext : bool, default: False
            If ``True``, use `.Text.set_transform_rotates_text` to ensure that
            label rotation is updated whenever the axes aspect changes.

        zorder : float or None, default: ``(2 + contour.get_zorder())``
            zorder of the contour labels.

        Returns
        -------
        labels
            A list of `.Text` instances for the labels.
        """

        # clabel basically takes the input arguments and uses them to
        # add a list of "label specific" attributes to the ContourSet
        # object.  These attributes are all of the form label* and names
        # should be fairly self explanatory.
        #
        # Once these attributes are set, clabel passes control to the
        # labels method (case of automatic label placement) or
        # `BlockingContourLabeler` (case of manual label placement).

        if fmt is None:
            fmt = ticker.ScalarFormatter(useOffset=False)
            fmt.create_dummy_axis()
        self.labelFmt = fmt
        self._use_clabeltext = use_clabeltext
        # Detect if manual selection is desired and remove from argument list.
        self.labelManual = manual
        self.rightside_up = rightside_up
        self._clabel_zorder = 2 + self.get_zorder() if zorder is None else zorder

        if levels is None:
            levels = self.levels
            indices = list(range(len(self.cvalues)))
        else:
            levlabs = list(levels)
            indices, levels = [], []
            for i, lev in enumerate(self.levels):
                if lev in levlabs:
                    indices.append(i)
                    levels.append(lev)
            if len(levels) < len(levlabs):
                raise ValueError(f"Specified levels {levlabs} don't match "
                                 f"available levels {self.levels}")
        self.labelLevelList = levels
        self.labelIndiceList = indices

        self._label_font_props = font_manager.FontProperties(size=fontsize)

        if colors is None:
            self.labelMappable = self
            self.labelCValueList = np.take(self.cvalues, self.labelIndiceList)
        else:
            cmap = mcolors.ListedColormap(colors, N=len(self.labelLevelList))
            self.labelCValueList = list(range(len(self.labelLevelList)))
            self.labelMappable = cm.ScalarMappable(cmap=cmap,
                                                   norm=mcolors.NoNorm())

        self.labelXYs = []

        if np.iterable(manual):
            for x, y in manual:
                self.add_label_near(x, y, inline, inline_spacing)
        elif manual:
            print('Select label locations manually using first mouse button.')
            print('End manual selection with second mouse button.')
            if not inline:
                print('Remove last label by clicking third mouse button.')
            mpl._blocking_input.blocking_input_loop(
                self.axes.figure, ["button_press_event", "key_press_event"],
                timeout=-1, handler=functools.partial(
                    _contour_labeler_event_handler,
                    self, inline, inline_spacing))
        else:
            self.labels(inline, inline_spacing)

        return cbook.silent_list('text.Text', self.labelTexts)

    @_api.deprecated("3.7", alternative="cs.labelTexts[0].get_font()")
    @property
    def labelFontProps(self):
        return self._label_font_props

    @_api.deprecated("3.7", alternative=(
        "[cs.labelTexts[0].get_font().get_size()] * len(cs.labelLevelList)"))
    @property
    def labelFontSizeList(self):
        return [self._label_font_props.get_size()] * len(self.labelLevelList)

    @_api.deprecated("3.7", alternative="cs.labelTexts")
    @property
    def labelTextsList(self):
        return cbook.silent_list('text.Text', self.labelTexts)

    def print_label(self, linecontour, labelwidth):
        """Return whether a contour is long enough to hold a label."""
        return (len(linecontour) > 10 * labelwidth
                or (len(linecontour)
                    and (np.ptp(linecontour, axis=0) > 1.2 * labelwidth).any()))

    def too_close(self, x, y, lw):
        """Return whether a label is already near this location."""
        thresh = (1.2 * lw) ** 2
        return any((x - loc[0]) ** 2 + (y - loc[1]) ** 2 < thresh
                   for loc in self.labelXYs)

    def _get_nth_label_width(self, nth):
        """Return the width of the *nth* label, in pixels."""
        fig = self.axes.figure
        renderer = fig._get_renderer()
        return (Text(0, 0,
                     self.get_text(self.labelLevelList[nth], self.labelFmt),
                     figure=fig, fontproperties=self._label_font_props)
                .get_window_extent(renderer).width)

    @_api.deprecated("3.7", alternative="Artist.set")
    def set_label_props(self, label, text, color):
        """Set the label properties - color, fontsize, text."""
        label.set_text(text)
        label.set_color(color)
        label.set_fontproperties(self._label_font_props)
        label.set_clip_box(self.axes.bbox)

    def get_text(self, lev, fmt):
        """Get the text of the label."""
        if isinstance(lev, str):
            return lev
        elif isinstance(fmt, dict):
            return fmt.get(lev, '%1.3f')
        elif callable(getattr(fmt, "format_ticks", None)):
            return fmt.format_ticks([*self.labelLevelList, lev])[-1]
        elif callable(fmt):
            return fmt(lev)
        else:
            return fmt % lev

    def locate_label(self, linecontour, labelwidth):
        """
        Find good place to draw a label (relatively flat part of the contour).
        """
        ctr_size = len(linecontour)
        n_blocks = int(np.ceil(ctr_size / labelwidth)) if labelwidth > 1 else 1
        block_size = ctr_size if n_blocks == 1 else int(labelwidth)
        # Split contour into blocks of length ``block_size``, filling the last
        # block by cycling the contour start (per `np.resize` semantics).  (Due
        # to cycling, the index returned is taken modulo ctr_size.)
        xx = np.resize(linecontour[:, 0], (n_blocks, block_size))
        yy = np.resize(linecontour[:, 1], (n_blocks, block_size))
        yfirst = yy[:, :1]
        ylast = yy[:, -1:]
        xfirst = xx[:, :1]
        xlast = xx[:, -1:]
        s = (yfirst - yy) * (xlast - xfirst) - (xfirst - xx) * (ylast - yfirst)
        l = np.hypot(xlast - xfirst, ylast - yfirst)
        # Ignore warning that divide by zero throws, as this is a valid option
        with np.errstate(divide='ignore', invalid='ignore'):
            distances = (abs(s) / l).sum(axis=-1)
        # Labels are drawn in the middle of the block (``hbsize``) where the
        # contour is the closest (per ``distances``) to a straight line, but
        # not `too_close()` to a preexisting label.
        hbsize = block_size // 2
        adist = np.argsort(distances)
        # If all candidates are `too_close()`, go back to the straightest part
        # (``adist[0]``).
        for idx in np.append(adist, adist[0]):
            x, y = xx[idx, hbsize], yy[idx, hbsize]
            if not self.too_close(x, y, labelwidth):
                break
        return x, y, (idx * block_size + hbsize) % ctr_size

    def _split_path_and_get_label_rotation(self, path, idx, screen_pos, lw, spacing=5):
        """
        Prepare for insertion of a label at index *idx* of *path*.

        Parameters
        ----------
        path : Path
            The path where the label will be inserted, in data space.
        idx : int
            The vertex index after which the label will be inserted.
        screen_pos : (float, float)
            The position where the label will be inserted, in screen space.
        lw : float
            The label width, in screen space.
        spacing : float
            Extra spacing around the label, in screen space.

        Returns
        -------
        path : Path
            The path, broken so that the label can be drawn over it.
        angle : float
            The rotation of the label.

        Notes
        -----
        Both tasks are done together to avoid calculating path lengths multiple times,
        which is relatively costly.

        The method used here involves computing the path length along the contour in
        pixel coordinates and then looking (label width / 2) away from central point to
        determine rotation and then to break contour if desired.  The extra spacing is
        taken into account when breaking the path, but not when computing the angle.
        """
        if hasattr(self, "_old_style_split_collections"):
            del self._old_style_split_collections  # Invalidate them.

        xys = path.vertices
        codes = path.codes

        # Insert a vertex at idx/pos (converting back to data space), if there isn't yet
        # a vertex there.  With infinite precision one could also always insert the
        # extra vertex (it will get masked out by the label below anyways), but floating
        # point inaccuracies (the point can have undergone a data->screen->data
        # transform loop) can slightly shift the point and e.g. shift the angle computed
        # below from exactly zero to nonzero.
        pos = self.get_transform().inverted().transform(screen_pos)
        if not np.allclose(pos, xys[idx]):
            xys = np.insert(xys, idx, pos, axis=0)
            codes = np.insert(codes, idx, Path.LINETO)

        # Find the connected component where the label will be inserted.  Note that a
        # path always starts with a MOVETO, and we consider there's an implicit
        # MOVETO (closing the last path) at the end.
        movetos = (codes == Path.MOVETO).nonzero()[0]
        start = movetos[movetos <= idx][-1]
        try:
            stop = movetos[movetos > idx][0]
        except IndexError:
            stop = len(codes)

        # Restrict ourselves to the connected component.
        cc_xys = xys[start:stop]
        idx -= start

        # If the path is closed, rotate it s.t. it starts at the label.
        is_closed_path = codes[stop - 1] == Path.CLOSEPOLY
        if is_closed_path:
            cc_xys = np.concatenate([xys[idx:-1], xys[:idx+1]])
            idx = 0

        # Like np.interp, but additionally vectorized over fp.
        def interp_vec(x, xp, fp): return [np.interp(x, xp, col) for col in fp.T]

        # Use cumulative path lengths ("cpl") as curvilinear coordinate along contour.
        screen_xys = self.get_transform().transform(cc_xys)
        path_cpls = np.insert(
            np.cumsum(np.hypot(*np.diff(screen_xys, axis=0).T)), 0, 0)
        path_cpls -= path_cpls[idx]

        # Use linear interpolation to get end coordinates of label.
        target_cpls = np.array([-lw/2, lw/2])
        if is_closed_path:  # For closed paths, target from the other end.
            target_cpls[0] += (path_cpls[-1] - path_cpls[0])
        (sx0, sx1), (sy0, sy1) = interp_vec(target_cpls, path_cpls, screen_xys)
        angle = np.rad2deg(np.arctan2(sy1 - sy0, sx1 - sx0))  # Screen space.
        if self.rightside_up:  # Fix angle so text is never upside-down
            angle = (angle + 90) % 180 - 90

        target_cpls += [-spacing, +spacing]  # Expand range by spacing.

        # Get indices near points of interest; use -1 as out of bounds marker.
        i0, i1 = np.interp(target_cpls, path_cpls, range(len(path_cpls)),
                           left=-1, right=-1)
        i0 = math.floor(i0)
        i1 = math.ceil(i1)
        (x0, x1), (y0, y1) = interp_vec(target_cpls, path_cpls, cc_xys)

        # Actually break contours (dropping zero-len parts).
        new_xy_blocks = []
        new_code_blocks = []
        if is_closed_path:
            if i0 != -1 and i1 != -1:
                new_xy_blocks.extend([[(x1, y1)], cc_xys[i1:i0+1], [(x0, y0)]])
                new_code_blocks.extend([[Path.MOVETO], [Path.LINETO] * (i0 + 2 - i1)])
        else:
            if i0 != -1:
                new_xy_blocks.extend([cc_xys[:i0 + 1], [(x0, y0)]])
                new_code_blocks.extend([[Path.MOVETO], [Path.LINETO] * (i0 + 1)])
            if i1 != -1:
                new_xy_blocks.extend([[(x1, y1)], cc_xys[i1:]])
                new_code_blocks.extend([
                    [Path.MOVETO], [Path.LINETO] * (len(cc_xys) - i1)])

        # Back to the full path.
        xys = np.concatenate([xys[:start], *new_xy_blocks, xys[stop:]])
        codes = np.concatenate([codes[:start], *new_code_blocks, codes[stop:]])

        return angle, Path(xys, codes)

    @_api.deprecated("3.8")
    def calc_label_rot_and_inline(self, slc, ind, lw, lc=None, spacing=5):
        """
        Calculate the appropriate label rotation given the linecontour
        coordinates in screen units, the index of the label location and the
        label width.

        If *lc* is not None or empty, also break contours and compute
        inlining.

        *spacing* is the empty space to leave around the label, in pixels.

        Both tasks are done together to avoid calculating path lengths
        multiple times, which is relatively costly.

        The method used here involves computing the path length along the
        contour in pixel coordinates and then looking approximately (label
        width / 2) away from central point to determine rotation and then to
        break contour if desired.
        """

        if lc is None:
            lc = []
        # Half the label width
        hlw = lw / 2.0

        # Check if closed and, if so, rotate contour so label is at edge
        closed = _is_closed_polygon(slc)
        if closed:
            slc = np.concatenate([slc[ind:-1], slc[:ind + 1]])
            if len(lc):  # Rotate lc also if not empty
                lc = np.concatenate([lc[ind:-1], lc[:ind + 1]])
            ind = 0

        # Calculate path lengths
        pl = np.zeros(slc.shape[0], dtype=float)
        dx = np.diff(slc, axis=0)
        pl[1:] = np.cumsum(np.hypot(dx[:, 0], dx[:, 1]))
        pl = pl - pl[ind]

        # Use linear interpolation to get points around label
        xi = np.array([-hlw, hlw])
        if closed:  # Look at end also for closed contours
            dp = np.array([pl[-1], 0])
        else:
            dp = np.zeros_like(xi)

        # Get angle of vector between the two ends of the label - must be
        # calculated in pixel space for text rotation to work correctly.
        (dx,), (dy,) = (np.diff(np.interp(dp + xi, pl, slc_col))
                        for slc_col in slc.T)
        rotation = np.rad2deg(np.arctan2(dy, dx))

        if self.rightside_up:
            # Fix angle so text is never upside-down
            rotation = (rotation + 90) % 180 - 90

        # Break contour if desired
        nlc = []
        if len(lc):
            # Expand range by spacing
            xi = dp + xi + np.array([-spacing, spacing])

            # Get (integer) indices near points of interest; use -1 as marker
            # for out of bounds.
            I = np.interp(xi, pl, np.arange(len(pl)), left=-1, right=-1)
            I = [np.floor(I[0]).astype(int), np.ceil(I[1]).astype(int)]
            if I[0] != -1:
                xy1 = [np.interp(xi[0], pl, lc_col) for lc_col in lc.T]
            if I[1] != -1:
                xy2 = [np.interp(xi[1], pl, lc_col) for lc_col in lc.T]

            # Actually break contours
            if closed:
                # This will remove contour if shorter than label
                if all(i != -1 for i in I):
                    nlc.append(np.row_stack([xy2, lc[I[1]:I[0]+1], xy1]))
            else:
                # These will remove pieces of contour if they have length zero
                if I[0] != -1:
                    nlc.append(np.row_stack([lc[:I[0]+1], xy1]))
                if I[1] != -1:
                    nlc.append(np.row_stack([xy2, lc[I[1]:]]))

            # The current implementation removes contours completely
            # covered by labels.  Uncomment line below to keep
            # original contour if this is the preferred behavior.
            # if not len(nlc): nlc = [lc]

        return rotation, nlc

    def add_label(self, x, y, rotation, lev, cvalue):
        """Add contour label without `.Text.set_transform_rotates_text`."""
        data_x, data_y = self.axes.transData.inverted().transform((x, y))
        t = Text(
            data_x, data_y,
            text=self.get_text(lev, self.labelFmt),
            rotation=rotation,
            horizontalalignment='center', verticalalignment='center',
            zorder=self._clabel_zorder,
            color=self.labelMappable.to_rgba(cvalue, alpha=self.get_alpha()),
            fontproperties=self._label_font_props,
            clip_box=self.axes.bbox)
        self.labelTexts.append(t)
        self.labelCValues.append(cvalue)
        self.labelXYs.append((x, y))
        # Add label to plot here - useful for manual mode label selection
        self.axes.add_artist(t)

    def add_label_clabeltext(self, x, y, rotation, lev, cvalue):
        """Add contour label with `.Text.set_transform_rotates_text`."""
        self.add_label(x, y, rotation, lev, cvalue)
        # Grab the last added text, and reconfigure its rotation.
        t = self.labelTexts[-1]
        data_rotation, = self.axes.transData.inverted().transform_angles(
            [rotation], [[x, y]])
        t.set(rotation=data_rotation, transform_rotates_text=True)

    def add_label_near(self, x, y, inline=True, inline_spacing=5,
                       transform=None):
        """
        Add a label near the point ``(x, y)``.

        Parameters
        ----------
        x, y : float
            The approximate location of the label.
        inline : bool, default: True
            If *True* remove the segment of the contour beneath the label.
        inline_spacing : int, default: 5
            Space in pixels to leave on each side of label when placing
            inline. This spacing will be exact for labels at locations where
            the contour is straight, less so for labels on curved contours.
        transform : `.Transform` or `False`, default: ``self.axes.transData``
            A transform applied to ``(x, y)`` before labeling.  The default
            causes ``(x, y)`` to be interpreted as data coordinates.  `False`
            is a synonym for `.IdentityTransform`; i.e. ``(x, y)`` should be
            interpreted as display coordinates.
        """

        if transform is None:
            transform = self.axes.transData
        if transform:
            x, y = transform.transform((x, y))

        idx_level_min, idx_vtx_min, proj = self._find_nearest_contour(
            (x, y), self.labelIndiceList)
        path = self._paths[idx_level_min]
        level = self.labelIndiceList.index(idx_level_min)
        label_width = self._get_nth_label_width(level)
        rotation, path = self._split_path_and_get_label_rotation(
            path, idx_vtx_min, proj, label_width, inline_spacing)
        self.add_label(*proj, rotation, self.labelLevelList[idx_level_min],
                       self.labelCValueList[idx_level_min])

        if inline:
            self._paths[idx_level_min] = path

    def pop_label(self, index=-1):
        """Defaults to removing last label, but any index can be supplied"""
        self.labelCValues.pop(index)
        t = self.labelTexts.pop(index)
        t.remove()

    def labels(self, inline, inline_spacing):

        if self._use_clabeltext:
            add_label = self.add_label_clabeltext
        else:
            add_label = self.add_label

        for idx, (icon, lev, cvalue) in enumerate(zip(
                self.labelIndiceList,
                self.labelLevelList,
                self.labelCValueList,
        )):
            trans = self.get_transform()
            label_width = self._get_nth_label_width(idx)
            additions = []
            for subpath in self._paths[icon]._iter_connected_components():
                screen_xys = trans.transform(subpath.vertices)
                # Check if long enough for a label
                if self.print_label(screen_xys, label_width):
                    x, y, idx = self.locate_label(screen_xys, label_width)
                    rotation, path = self._split_path_and_get_label_rotation(
                        subpath, idx, (x, y),
                        label_width, inline_spacing)
                    add_label(x, y, rotation, lev, cvalue)  # Really add label.
                    if inline:  # If inline, add new contours
                        additions.append(path)
                else:  # If not adding label, keep old path
                    additions.append(subpath)
            # After looping over all segments on a contour, replace old path by new one
            # if inlining.
            if inline:
                self._paths[icon] = Path.make_compound_path(*additions)

    def remove(self):
        super().remove()
        for text in self.labelTexts:
            text.remove()


def _is_closed_polygon(X):
    """
    Return whether first and last object in a sequence are the same. These are
    presumably coordinates on a polygonal curve, in which case this function
    tests if that curve is closed.
    """
    return np.allclose(X[0], X[-1], rtol=1e-10, atol=1e-13)


def _find_closest_point_on_path(xys, p):
    """
    Parameters
    ----------
    xys : (N, 2) array-like
        Coordinates of vertices.
    p : (float, float)
        Coordinates of point.

    Returns
    -------
    d2min : float
        Minimum square distance of *p* to *xys*.
    proj : (float, float)
        Projection of *p* onto *xys*.
    imin : (int, int)
        Consecutive indices of vertices of segment in *xys* where *proj* is.
        Segments are considered as including their end-points; i.e. if the
        closest point on the path is a node in *xys* with index *i*, this
        returns ``(i-1, i)``.  For the special case where *xys* is a single
        point, this returns ``(0, 0)``.
    """
    if len(xys) == 1:
        return (((p - xys[0]) ** 2).sum(), xys[0], (0, 0))
    dxys = xys[1:] - xys[:-1]  # Individual segment vectors.
    norms = (dxys ** 2).sum(axis=1)
    norms[norms == 0] = 1  # For zero-length segment, replace 0/0 by 0/1.
    rel_projs = np.clip(  # Project onto each segment in relative 0-1 coords.
        ((p - xys[:-1]) * dxys).sum(axis=1) / norms,
        0, 1)[:, None]
    projs = xys[:-1] + rel_projs * dxys  # Projs. onto each segment, in (x, y).
    d2s = ((projs - p) ** 2).sum(axis=1)  # Squared distances.
    imin = np.argmin(d2s)
    return (d2s[imin], projs[imin], (imin, imin+1))


_docstring.interpd.update(contour_set_attributes=r"""
Attributes
----------
ax : `~matplotlib.axes.Axes`
    The Axes object in which the contours are drawn.

collections : `.silent_list` of `.PathCollection`\s
    The `.Artist`\s representing the contour. This is a list of
    `.PathCollection`\s for both line and filled contours.

levels : array
    The values of the contour levels.

layers : array
    Same as levels for line contours; half-way between
    levels for filled contours.  See ``ContourSet._process_colors``.
""")


@_docstring.dedent_interpd
class ContourSet(ContourLabeler, mcoll.Collection):
    """
    Store a set of contour lines or filled regions.

    User-callable method: `~.Axes.clabel`

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`

    levels : [level0, level1, ..., leveln]
        A list of floating point numbers indicating the contour levels.

    allsegs : [level0segs, level1segs, ...]
        List of all the polygon segments for all the *levels*.
        For contour lines ``len(allsegs) == len(levels)``, and for
        filled contour regions ``len(allsegs) = len(levels)-1``. The lists
        should look like ::

            level0segs = [polygon0, polygon1, ...]
            polygon0 = [[x0, y0], [x1, y1], ...]

    allkinds : ``None`` or [level0kinds, level1kinds, ...]
        Optional list of all the polygon vertex kinds (code types), as
        described and used in Path. This is used to allow multiply-
        connected paths such as holes within filled polygons.
        If not ``None``, ``len(allkinds) == len(allsegs)``. The lists
        should look like ::

            level0kinds = [polygon0kinds, ...]
            polygon0kinds = [vertexcode0, vertexcode1, ...]

        If *allkinds* is not ``None``, usually all polygons for a
        particular contour level are grouped together so that
        ``level0segs = [polygon0]`` and ``level0kinds = [polygon0kinds]``.

    **kwargs
        Keyword arguments are as described in the docstring of
        `~.Axes.contour`.

    %(contour_set_attributes)s
    """

    def __init__(self, ax, *args,
                 levels=None, filled=False, linewidths=None, linestyles=None,
                 hatches=(None,), alpha=None, origin=None, extent=None,
                 cmap=None, colors=None, norm=None, vmin=None, vmax=None,
                 extend='neither', antialiased=None, nchunk=0, locator=None,
                 transform=None, negative_linestyles=None, clip_path=None,
                 **kwargs):
        """
        Draw contour lines or filled regions, depending on
        whether keyword arg *filled* is ``False`` (default) or ``True``.

        Call signature::

            ContourSet(ax, levels, allsegs, [allkinds], **kwargs)

        Parameters
        ----------
        ax : `~matplotlib.axes.Axes`
            The `~.axes.Axes` object to draw on.

        levels : [level0, level1, ..., leveln]
            A list of floating point numbers indicating the contour
            levels.

        allsegs : [level0segs, level1segs, ...]
            List of all the polygon segments for all the *levels*.
            For contour lines ``len(allsegs) == len(levels)``, and for
            filled contour regions ``len(allsegs) = len(levels)-1``. The lists
            should look like ::

                level0segs = [polygon0, polygon1, ...]
                polygon0 = [[x0, y0], [x1, y1], ...]

        allkinds : [level0kinds, level1kinds, ...], optional
            Optional list of all the polygon vertex kinds (code types), as
            described and used in Path. This is used to allow multiply-
            connected paths such as holes within filled polygons.
            If not ``None``, ``len(allkinds) == len(allsegs)``. The lists
            should look like ::

                level0kinds = [polygon0kinds, ...]
                polygon0kinds = [vertexcode0, vertexcode1, ...]

            If *allkinds* is not ``None``, usually all polygons for a
            particular contour level are grouped together so that
            ``level0segs = [polygon0]`` and ``level0kinds = [polygon0kinds]``.

        **kwargs
            Keyword arguments are as described in the docstring of
            `~.Axes.contour`.
        """
        if antialiased is None and filled:
            # Eliminate artifacts; we are not stroking the boundaries.
            antialiased = False
            # The default for line contours will be taken from the
            # LineCollection default, which uses :rc:`lines.antialiased`.
        super().__init__(
            antialiaseds=antialiased,
            alpha=alpha,
            clip_path=clip_path,
            transform=transform,
        )
        self.axes = ax
        self.levels = levels
        self.filled = filled
        self.hatches = hatches
        self.origin = origin
        self.extent = extent
        self.colors = colors
        self.extend = extend

        self.nchunk = nchunk
        self.locator = locator
        if (isinstance(norm, mcolors.LogNorm)
                or isinstance(self.locator, ticker.LogLocator)):
            self.logscale = True
            if norm is None:
                norm = mcolors.LogNorm()
        else:
            self.logscale = False

        _api.check_in_list([None, 'lower', 'upper', 'image'], origin=origin)
        if self.extent is not None and len(self.extent) != 4:
            raise ValueError(
                "If given, 'extent' must be None or (x0, x1, y0, y1)")
        if self.colors is not None and cmap is not None:
            raise ValueError('Either colors or cmap must be None')
        if self.origin == 'image':
            self.origin = mpl.rcParams['image.origin']

        self._orig_linestyles = linestyles  # Only kept for user access.
        self.negative_linestyles = negative_linestyles
        # If negative_linestyles was not defined as a keyword argument, define
        # negative_linestyles with rcParams
        if self.negative_linestyles is None:
            self.negative_linestyles = \
                mpl.rcParams['contour.negative_linestyle']

        kwargs = self._process_args(*args, **kwargs)
        self._process_levels()

        self._extend_min = self.extend in ['min', 'both']
        self._extend_max = self.extend in ['max', 'both']
        if self.colors is not None:
            ncolors = len(self.levels)
            if self.filled:
                ncolors -= 1
            i0 = 0

            # Handle the case where colors are given for the extended
            # parts of the contour.

            use_set_under_over = False
            # if we are extending the lower end, and we've been given enough
            # colors then skip the first color in the resulting cmap. For the
            # extend_max case we don't need to worry about passing more colors
            # than ncolors as ListedColormap will clip.
            total_levels = (ncolors +
                            int(self._extend_min) +
                            int(self._extend_max))
            if (len(self.colors) == total_levels and
                    (self._extend_min or self._extend_max)):
                use_set_under_over = True
                if self._extend_min:
                    i0 = 1

            cmap = mcolors.ListedColormap(self.colors[i0:None], N=ncolors)

            if use_set_under_over:
                if self._extend_min:
                    cmap.set_under(self.colors[0])
                if self._extend_max:
                    cmap.set_over(self.colors[-1])

        # label lists must be initialized here
        self.labelTexts = []
        self.labelCValues = []

        self.set_cmap(cmap)
        if norm is not None:
            self.set_norm(norm)
        if vmin is not None:
            self.norm.vmin = vmin
        if vmax is not None:
            self.norm.vmax = vmax
        self._process_colors()

        if self._paths is None:
            self._paths = self._make_paths_from_contour_generator()

        if self.filled:
            if linewidths is not None:
                _api.warn_external('linewidths is ignored by contourf')
            # Lower and upper contour levels.
            lowers, uppers = self._get_lowers_and_uppers()
            self.set(
                edgecolor="none",
                # Default zorder taken from Collection
                zorder=kwargs.pop("zorder", 1),
            )

        else:
            self.set(
                facecolor="none",
                linewidths=self._process_linewidths(linewidths),
                linestyle=self._process_linestyles(linestyles),
                # Default zorder taken from LineCollection, which is higher
                # than for filled contours so that lines are displayed on top.
                zorder=kwargs.pop("zorder", 2),
                label="_nolegend_",
            )

        self.axes.add_collection(self, autolim=False)
        self.sticky_edges.x[:] = [self._mins[0], self._maxs[0]]
        self.sticky_edges.y[:] = [self._mins[1], self._maxs[1]]
        self.axes.update_datalim([self._mins, self._maxs])
        self.axes.autoscale_view(tight=True)

        self.changed()  # set the colors

        if kwargs:
            _api.warn_external(
                'The following kwargs were not used by contour: ' +
                ", ".join(map(repr, kwargs))
            )

    allsegs = _api.deprecated("3.8", pending=True)(property(lambda self: [
        p.vertices for c in self.collections for p in c.get_paths()]))
    allkinds = _api.deprecated("3.8", pending=True)(property(lambda self: [
        p.codes for c in self.collections for p in c.get_paths()]))
    tcolors = _api.deprecated("3.8")(property(lambda self: [
        (tuple(rgba),) for rgba in self.to_rgba(self.cvalues, self.alpha)]))
    tlinewidths = _api.deprecated("3.8")(property(lambda self: [
        (w,) for w in self.get_linewidths()]))
    alpha = property(lambda self: self.get_alpha())
    linestyles = property(lambda self: self._orig_linestyles)

    @_api.deprecated("3.8")
    @property
    def collections(self):
        # On access, make oneself invisible and instead add the old-style collections
        # (one PathCollection per level).  We do not try to further split contours into
        # connected components as we already lost track of what pairs of contours need
        # to be considered as single units to draw filled regions with holes.
        if not hasattr(self, "_old_style_split_collections"):
            self.set_visible(False)
            fcs = self.get_facecolor()
            ecs = self.get_edgecolor()
            lws = self.get_linewidth()
            lss = self.get_linestyle()
            self._old_style_split_collections = []
            for idx, path in enumerate(self._paths):
                pc = mcoll.PathCollection(
                    [path] if len(path.vertices) else [],
                    alpha=self.get_alpha(),
                    antialiaseds=self._antialiaseds[idx % len(self._antialiaseds)],
                    transform=self.get_transform(),
                    zorder=self.get_zorder(),
                    label="_nolegend_",
                    facecolor=fcs[idx] if len(fcs) else "none",
                    edgecolor=ecs[idx] if len(ecs) else "none",
                    linewidths=[lws[idx % len(lws)]],
                    linestyles=[lss[idx % len(lss)]],
                )
                if self.filled:
                    pc.set(hatch=self.hatches[idx % len(self.hatches)])
                self._old_style_split_collections.append(pc)
            for col in self._old_style_split_collections:
                self.axes.add_collection(col)
        return self._old_style_split_collections

    def get_transform(self):
        """Return the `.Transform` instance used by this ContourSet."""
        if self._transform is None:
            self._transform = self.axes.transData
        elif (not isinstance(self._transform, mtransforms.Transform)
              and hasattr(self._transform, '_as_mpl_transform')):
            self._transform = self._transform._as_mpl_transform(self.axes)
        return self._transform

    def __getstate__(self):
        state = self.__dict__.copy()
        # the C object _contour_generator cannot currently be pickled. This
        # isn't a big issue as it is not actually used once the contour has
        # been calculated.
        state['_contour_generator'] = None
        return state

    def legend_elements(self, variable_name='x', str_format=str):
        """
        Return a list of artists and labels suitable for passing through
        to `~.Axes.legend` which represent this ContourSet.

        The labels have the form "0 < x <= 1" stating the data ranges which
        the artists represent.

        Parameters
        ----------
        variable_name : str
            The string used inside the inequality used on the labels.
        str_format : function: float -> str
            Function used to format the numbers in the labels.

        Returns
        -------
        artists : list[`.Artist`]
            A list of the artists.
        labels : list[str]
            A list of the labels.
        """
        artists = []
        labels = []

        if self.filled:
            lowers, uppers = self._get_lowers_and_uppers()
            n_levels = len(self._paths)
            for idx in range(n_levels):
                artists.append(mpatches.Rectangle(
                    (0, 0), 1, 1,
                    facecolor=self.get_facecolor()[idx],
                    hatch=self.hatches[idx % len(self.hatches)],
                ))
                lower = str_format(lowers[idx])
                upper = str_format(uppers[idx])
                if idx == 0 and self.extend in ('min', 'both'):
                    labels.append(fr'${variable_name} \leq {lower}s$')
                elif idx == n_levels - 1 and self.extend in ('max', 'both'):
                    labels.append(fr'${variable_name} > {upper}s$')
                else:
                    labels.append(fr'${lower} < {variable_name} \leq {upper}$')
        else:
            for idx, level in enumerate(self.levels):
                artists.append(Line2D(
                    [], [],
                    color=self.get_edgecolor()[idx],
                    linewidth=self.get_linewidths()[idx],
                    linestyle=self.get_linestyles()[idx],
                ))
                labels.append(fr'${variable_name} = {str_format(level)}$')

        return artists, labels

    def _process_args(self, *args, **kwargs):
        """
        Process *args* and *kwargs*; override in derived classes.

        Must set self.levels, self.zmin and self.zmax, and update axes limits.
        """
        self.levels = args[0]
        allsegs = args[1]
        allkinds = args[2] if len(args) > 2 else None
        self.zmax = np.max(self.levels)
        self.zmin = np.min(self.levels)

        if allkinds is None:
            allkinds = [[None] * len(segs) for segs in allsegs]

        # Check lengths of levels and allsegs.
        if self.filled:
            if len(allsegs) != len(self.levels) - 1:
                raise ValueError('must be one less number of segments as '
                                 'levels')
        else:
            if len(allsegs) != len(self.levels):
                raise ValueError('must be same number of segments as levels')

        # Check length of allkinds.
        if len(allkinds) != len(allsegs):
            raise ValueError('allkinds has different length to allsegs')

        # Determine x, y bounds and update axes data limits.
        flatseglist = [s for seg in allsegs for s in seg]
        points = np.concatenate(flatseglist, axis=0)
        self._mins = points.min(axis=0)
        self._maxs = points.max(axis=0)

        # Each entry in (allsegs, allkinds) is a list of (segs, kinds): segs is a list
        # of (N, 2) arrays of xy coordinates, kinds is a list of arrays of corresponding
        # pathcodes.  However, kinds can also be None; in which case all paths in that
        # list are codeless (this case is normalized above).  These lists are used to
        # construct paths, which then get concatenated.
        self._paths = [Path.make_compound_path(*map(Path, segs, kinds))
                       for segs, kinds in zip(allsegs, allkinds)]

        return kwargs

    def _make_paths_from_contour_generator(self):
        """Compute ``paths`` using C extension."""
        if self._paths is not None:
            return self._paths
        paths = []
        empty_path = Path(np.empty((0, 2)))
        if self.filled:
            lowers, uppers = self._get_lowers_and_uppers()
            for level, level_upper in zip(lowers, uppers):
                vertices, kinds = \
                    self._contour_generator.create_filled_contour(
                        level, level_upper)
                paths.append(Path(np.concatenate(vertices), np.concatenate(kinds))
                             if len(vertices) else empty_path)
        else:
            for level in self.levels:
                vertices, kinds = self._contour_generator.create_contour(level)
                paths.append(Path(np.concatenate(vertices), np.concatenate(kinds))
                             if len(vertices) else empty_path)
        return paths

    def _get_lowers_and_uppers(self):
        """
        Return ``(lowers, uppers)`` for filled contours.
        """
        lowers = self._levels[:-1]
        if self.zmin == lowers[0]:
            # Include minimum values in lowest interval
            lowers = lowers.copy()  # so we don't change self._levels
            if self.logscale:
                lowers[0] = 0.99 * self.zmin
            else:
                lowers[0] -= 1
        uppers = self._levels[1:]
        return (lowers, uppers)

    def changed(self):
        if not hasattr(self, "cvalues"):
            self._process_colors()  # Sets cvalues.
        # Force an autoscale immediately because self.to_rgba() calls
        # autoscale_None() internally with the data passed to it,
        # so if vmin/vmax are not set yet, this would override them with
        # content from *cvalues* rather than levels like we want
        self.norm.autoscale_None(self.levels)
        self.set_array(self.cvalues)
        self.update_scalarmappable()
        alphas = np.broadcast_to(self.get_alpha(), len(self.cvalues))
        for label, cv, alpha in zip(self.labelTexts, self.labelCValues, alphas):
            label.set_alpha(alpha)
            label.set_color(self.labelMappable.to_rgba(cv))
        super().changed()

    def _autolev(self, N):
        """
        Select contour levels to span the data.

        The target number of levels, *N*, is used only when the
        scale is not log and default locator is used.

        We need two more levels for filled contours than for
        line contours, because for the latter we need to specify
        the lower and upper boundary of each range. For example,
        a single contour boundary, say at z = 0, requires only
        one contour line, but two filled regions, and therefore
        three levels to provide boundaries for both regions.
        """
        if self.locator is None:
            if self.logscale:
                self.locator = ticker.LogLocator()
            else:
                self.locator = ticker.MaxNLocator(N + 1, min_n_ticks=1)

        lev = self.locator.tick_values(self.zmin, self.zmax)

        try:
            if self.locator._symmetric:
                return lev
        except AttributeError:
            pass

        # Trim excess levels the locator may have supplied.
        under = np.nonzero(lev < self.zmin)[0]
        i0 = under[-1] if len(under) else 0
        over = np.nonzero(lev > self.zmax)[0]
        i1 = over[0] + 1 if len(over) else len(lev)
        if self.extend in ('min', 'both'):
            i0 += 1
        if self.extend in ('max', 'both'):
            i1 -= 1

        if i1 - i0 < 3:
            i0, i1 = 0, len(lev)

        return lev[i0:i1]

    def _process_contour_level_args(self, args, z_dtype):
        """
        Determine the contour levels and store in self.levels.
        """
        if self.levels is None:
            if args:
                levels_arg = args[0]
            elif np.issubdtype(z_dtype, bool):
                if self.filled:
                    levels_arg = [0, .5, 1]
                else:
                    levels_arg = [.5]
            else:
                levels_arg = 7  # Default, hard-wired.
        else:
            levels_arg = self.levels
        if isinstance(levels_arg, Integral):
            self.levels = self._autolev(levels_arg)
        else:
            self.levels = np.asarray(levels_arg, np.float64)
        if self.filled and len(self.levels) < 2:
            raise ValueError("Filled contours require at least 2 levels.")
        if len(self.levels) > 1 and np.min(np.diff(self.levels)) <= 0.0:
            raise ValueError("Contour levels must be increasing")

    def _process_levels(self):
        """
        Assign values to :attr:`layers` based on :attr:`levels`,
        adding extended layers as needed if contours are filled.

        For line contours, layers simply coincide with levels;
        a line is a thin layer.  No extended levels are needed
        with line contours.
        """
        # Make a private _levels to include extended regions; we
        # want to leave the original levels attribute unchanged.
        # (Colorbar needs this even for line contours.)
        self._levels = list(self.levels)

        if self.logscale:
            lower, upper = 1e-250, 1e250
        else:
            lower, upper = -1e250, 1e250

        if self.extend in ('both', 'min'):
            self._levels.insert(0, lower)
        if self.extend in ('both', 'max'):
            self._levels.append(upper)
        self._levels = np.asarray(self._levels)

        if not self.filled:
            self.layers = self.levels
            return

        # Layer values are mid-way between levels in screen space.
        if self.logscale:
            # Avoid overflow by taking sqrt before multiplying.
            self.layers = (np.sqrt(self._levels[:-1])
                           * np.sqrt(self._levels[1:]))
        else:
            self.layers = 0.5 * (self._levels[:-1] + self._levels[1:])

    def _process_colors(self):
        """
        Color argument processing for contouring.

        Note that we base the colormapping on the contour levels
        and layers, not on the actual range of the Z values.  This
        means we don't have to worry about bad values in Z, and we
        always have the full dynamic range available for the selected
        levels.

        The color is based on the midpoint of the layer, except for
        extended end layers.  By default, the norm vmin and vmax
        are the extreme values of the non-extended levels.  Hence,
        the layer color extremes are not the extreme values of
        the colormap itself, but approach those values as the number
        of levels increases.  An advantage of this scheme is that
        line contours, when added to filled contours, take on
        colors that are consistent with those of the filled regions;
        for example, a contour line on the boundary between two
        regions will have a color intermediate between those
        of the regions.

        """
        self.monochrome = self.cmap.monochrome
        if self.colors is not None:
            # Generate integers for direct indexing.
            i0, i1 = 0, len(self.levels)
            if self.filled:
                i1 -= 1
                # Out of range indices for over and under:
                if self.extend in ('both', 'min'):
                    i0 -= 1
                if self.extend in ('both', 'max'):
                    i1 += 1
            self.cvalues = list(range(i0, i1))
            self.set_norm(mcolors.NoNorm())
        else:
            self.cvalues = self.layers
        self.norm.autoscale_None(self.levels)
        self.set_array(self.cvalues)
        self.update_scalarmappable()
        if self.extend in ('both', 'max', 'min'):
            self.norm.clip = False

    def _process_linewidths(self, linewidths):
        Nlev = len(self.levels)
        if linewidths is None:
            default_linewidth = mpl.rcParams['contour.linewidth']
            if default_linewidth is None:
                default_linewidth = mpl.rcParams['lines.linewidth']
            return [default_linewidth] * Nlev
        elif not np.iterable(linewidths):
            return [linewidths] * Nlev
        else:
            linewidths = list(linewidths)
            return (linewidths * math.ceil(Nlev / len(linewidths)))[:Nlev]

    def _process_linestyles(self, linestyles):
        Nlev = len(self.levels)
        if linestyles is None:
            tlinestyles = ['solid'] * Nlev
            if self.monochrome:
                eps = - (self.zmax - self.zmin) * 1e-15
                for i, lev in enumerate(self.levels):
                    if lev < eps:
                        tlinestyles[i] = self.negative_linestyles
        else:
            if isinstance(linestyles, str):
                tlinestyles = [linestyles] * Nlev
            elif np.iterable(linestyles):
                tlinestyles = list(linestyles)
                if len(tlinestyles) < Nlev:
                    nreps = int(np.ceil(Nlev / len(linestyles)))
                    tlinestyles = tlinestyles * nreps
                if len(tlinestyles) > Nlev:
                    tlinestyles = tlinestyles[:Nlev]
            else:
                raise ValueError("Unrecognized type for linestyles kwarg")
        return tlinestyles

    def _find_nearest_contour(self, xy, indices=None):
        """
        Find the point in the unfilled contour plot that is closest (in screen
        space) to point *xy*.

        Parameters
        ----------
        xy : tuple[float, float]
            The reference point (in screen space).
        indices : list of int or None, default: None
            Indices of contour levels to consider.  If None (the default), all levels
            are considered.

        Returns
        -------
        idx_level_min : int
            The index of the contour level closest to *xy*.
        idx_vtx_min : int
            The index of the `.Path` segment closest to *xy* (at that level).
        proj : (float, float)
            The point in the contour plot closest to *xy*.
        """

        # Convert each contour segment to pixel coordinates and then compare the given
        # point to those coordinates for each contour. This is fast enough in normal
        # cases, but speedups may be possible.

        if self.filled:
            raise ValueError("Method does not support filled contours")

        if indices is None:
            indices = range(len(self._paths))

        d2min = np.inf
        idx_level_min = idx_vtx_min = proj_min = None

        for idx_level in indices:
            path = self._paths[idx_level]
            if not len(path.vertices):
                continue
            lc = self.get_transform().transform(path.vertices)
            d2, proj, leg = _find_closest_point_on_path(lc, xy)
            if d2 < d2min:
                d2min = d2
                idx_level_min = idx_level
                idx_vtx_min = leg[1]
                proj_min = proj

        return idx_level_min, idx_vtx_min, proj_min

    @_api.deprecated("3.8")
    def find_nearest_contour(self, x, y, indices=None, pixel=True):
        """
        Find the point in the contour plot that is closest to ``(x, y)``.

        This method does not support filled contours.

        Parameters
        ----------
        x, y : float
            The reference point.
        indices : list of int or None, default: None
            Indices of contour levels to consider.  If None (the default), all
            levels are considered.
        pixel : bool, default: True
            If *True*, measure distance in pixel (screen) space, which is
            useful for manual contour labeling; else, measure distance in axes
            space.

        Returns
        -------
        contour : `.Collection`
            The contour that is closest to ``(x, y)``.
        segment : int
            The index of the `.Path` in *contour* that is closest to
            ``(x, y)``.
        index : int
            The index of the path segment in *segment* that is closest to
            ``(x, y)``.
        xmin, ymin : float
            The point in the contour plot that is closest to ``(x, y)``.
        d2 : float
            The squared distance from ``(xmin, ymin)`` to ``(x, y)``.
        """

        # This function uses a method that is probably quite
        # inefficient based on converting each contour segment to
        # pixel coordinates and then comparing the given point to
        # those coordinates for each contour.  This will probably be
        # quite slow for complex contours, but for normal use it works
        # sufficiently well that the time is not noticeable.
        # Nonetheless, improvements could probably be made.

        if self.filled:
            raise ValueError("Method does not support filled contours.")

        if indices is None:
            indices = range(len(self.collections))

        d2min = np.inf
        conmin = None
        segmin = None
        imin = None
        xmin = None
        ymin = None

        point = np.array([x, y])

        for icon in indices:
            con = self.collections[icon]
            trans = con.get_transform()
            paths = con.get_paths()

            for segNum, linepath in enumerate(paths):
                lc = linepath.vertices
                # transfer all data points to screen coordinates if desired
                if pixel:
                    lc = trans.transform(lc)

                d2, xc, leg = _find_closest_point_on_path(lc, point)
                if d2 < d2min:
                    d2min = d2
                    conmin = icon
                    segmin = segNum
                    imin = leg[1]
                    xmin = xc[0]
                    ymin = xc[1]

        return (conmin, segmin, imin, xmin, ymin, d2min)

    def draw(self, renderer):
        paths = self._paths
        n_paths = len(paths)
        if not self.filled or all(hatch is None for hatch in self.hatches):
            super().draw(renderer)
            return
        # In presence of hatching, draw contours one at a time.
        for idx in range(n_paths):
            with cbook._setattr_cm(self, _paths=[paths[idx]]), self._cm_set(
                hatch=self.hatches[idx % len(self.hatches)],
                array=[self.get_array()[idx]],
                linewidths=[self.get_linewidths()[idx % len(self.get_linewidths())]],
                linestyles=[self.get_linestyles()[idx % len(self.get_linestyles())]],
            ):
                super().draw(renderer)


@_docstring.dedent_interpd
class QuadContourSet(ContourSet):
    """
    Create and store a set of contour lines or filled regions.

    This class is typically not instantiated directly by the user but by
    `~.Axes.contour` and `~.Axes.contourf`.

    %(contour_set_attributes)s
    """

    def _process_args(self, *args, corner_mask=None, algorithm=None, **kwargs):
        """
        Process args and kwargs.
        """
        if args and isinstance(args[0], QuadContourSet):
            if self.levels is None:
                self.levels = args[0].levels
            self.zmin = args[0].zmin
            self.zmax = args[0].zmax
            self._corner_mask = args[0]._corner_mask
            contour_generator = args[0]._contour_generator
            self._mins = args[0]._mins
            self._maxs = args[0]._maxs
            self._algorithm = args[0]._algorithm
        else:
            import contourpy

            if algorithm is None:
                algorithm = mpl.rcParams['contour.algorithm']
            mpl.rcParams.validate["contour.algorithm"](algorithm)
            self._algorithm = algorithm

            if corner_mask is None:
                if self._algorithm == "mpl2005":
                    # mpl2005 does not support corner_mask=True so if not
                    # specifically requested then disable it.
                    corner_mask = False
                else:
                    corner_mask = mpl.rcParams['contour.corner_mask']
            self._corner_mask = corner_mask

            x, y, z = self._contour_args(args, kwargs)

            contour_generator = contourpy.contour_generator(
                x, y, z, name=self._algorithm, corner_mask=self._corner_mask,
                line_type=contourpy.LineType.SeparateCode,
                fill_type=contourpy.FillType.OuterCode,
                chunk_size=self.nchunk)

            t = self.get_transform()

            # if the transform is not trans data, and some part of it
            # contains transData, transform the xs and ys to data coordinates
            if (t != self.axes.transData and
                    any(t.contains_branch_seperately(self.axes.transData))):
                trans_to_data = t - self.axes.transData
                pts = np.vstack([x.flat, y.flat]).T
                transformed_pts = trans_to_data.transform(pts)
                x = transformed_pts[..., 0]
                y = transformed_pts[..., 1]

            self._mins = [ma.min(x), ma.min(y)]
            self._maxs = [ma.max(x), ma.max(y)]

        self._contour_generator = contour_generator

        return kwargs

    def _contour_args(self, args, kwargs):
        if self.filled:
            fn = 'contourf'
        else:
            fn = 'contour'
        nargs = len(args)

        if 0 < nargs <= 2:
            z, *args = args
            z = ma.asarray(z)
            x, y = self._initialize_x_y(z)
        elif 2 < nargs <= 4:
            x, y, z_orig, *args = args
            x, y, z = self._check_xyz(x, y, z_orig, kwargs)

        else:
            raise _api.nargs_error(fn, takes="from 1 to 4", given=nargs)
        z = ma.masked_invalid(z, copy=False)
        self.zmax = z.max().astype(float)
        self.zmin = z.min().astype(float)
        if self.logscale and self.zmin <= 0:
            z = ma.masked_where(z <= 0, z)
            _api.warn_external('Log scale: values of z <= 0 have been masked')
            self.zmin = z.min().astype(float)
        self._process_contour_level_args(args, z.dtype)
        return (x, y, z)

    def _check_xyz(self, x, y, z, kwargs):
        """
        Check that the shapes of the input arrays match; if x and y are 1D,
        convert them to 2D using meshgrid.
        """
        x, y = self.axes._process_unit_info([("x", x), ("y", y)], kwargs)

        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        z = ma.asarray(z)

        if z.ndim != 2:
            raise TypeError(f"Input z must be 2D, not {z.ndim}D")
        if z.shape[0] < 2 or z.shape[1] < 2:
            raise TypeError(f"Input z must be at least a (2, 2) shaped array, "
                            f"but has shape {z.shape}")
        Ny, Nx = z.shape

        if x.ndim != y.ndim:
            raise TypeError(f"Number of dimensions of x ({x.ndim}) and y "
                            f"({y.ndim}) do not match")
        if x.ndim == 1:
            nx, = x.shape
            ny, = y.shape
            if nx != Nx:
                raise TypeError(f"Length of x ({nx}) must match number of "
                                f"columns in z ({Nx})")
            if ny != Ny:
                raise TypeError(f"Length of y ({ny}) must match number of "
                                f"rows in z ({Ny})")
            x, y = np.meshgrid(x, y)
        elif x.ndim == 2:
            if x.shape != z.shape:
                raise TypeError(
                    f"Shapes of x {x.shape} and z {z.shape} do not match")
            if y.shape != z.shape:
                raise TypeError(
                    f"Shapes of y {y.shape} and z {z.shape} do not match")
        else:
            raise TypeError(f"Inputs x and y must be 1D or 2D, not {x.ndim}D")

        return x, y, z

    def _initialize_x_y(self, z):
        """
        Return X, Y arrays such that contour(Z) will match imshow(Z)
        if origin is not None.
        The center of pixel Z[i, j] depends on origin:
        if origin is None, x = j, y = i;
        if origin is 'lower', x = j + 0.5, y = i + 0.5;
        if origin is 'upper', x = j + 0.5, y = Nrows - i - 0.5
        If extent is not None, x and y will be scaled to match,
        as in imshow.
        If origin is None and extent is not None, then extent
        will give the minimum and maximum values of x and y.
        """
        if z.ndim != 2:
            raise TypeError(f"Input z must be 2D, not {z.ndim}D")
        elif z.shape[0] < 2 or z.shape[1] < 2:
            raise TypeError(f"Input z must be at least a (2, 2) shaped array, "
                            f"but has shape {z.shape}")
        else:
            Ny, Nx = z.shape
        if self.origin is None:  # Not for image-matching.
            if self.extent is None:
                return np.meshgrid(np.arange(Nx), np.arange(Ny))
            else:
                x0, x1, y0, y1 = self.extent
                x = np.linspace(x0, x1, Nx)
                y = np.linspace(y0, y1, Ny)
                return np.meshgrid(x, y)
        # Match image behavior:
        if self.extent is None:
            x0, x1, y0, y1 = (0, Nx, 0, Ny)
        else:
            x0, x1, y0, y1 = self.extent
        dx = (x1 - x0) / Nx
        dy = (y1 - y0) / Ny
        x = x0 + (np.arange(Nx) + 0.5) * dx
        y = y0 + (np.arange(Ny) + 0.5) * dy
        if self.origin == 'upper':
            y = y[::-1]
        return np.meshgrid(x, y)


_docstring.interpd.update(contour_doc="""
`.contour` and `.contourf` draw contour lines and filled contours,
respectively.  Except as noted, function signatures and return values
are the same for both versions.

Parameters
----------
X, Y : array-like, optional
    The coordinates of the values in *Z*.

    *X* and *Y* must both be 2D with the same shape as *Z* (e.g.
    created via `numpy.meshgrid`), or they must both be 1-D such
    that ``len(X) == N`` is the number of columns in *Z* and
    ``len(Y) == M`` is the number of rows in *Z*.

    *X* and *Y* must both be ordered monotonically.

    If not given, they are assumed to be integer indices, i.e.
    ``X = range(N)``, ``Y = range(M)``.

Z : (M, N) array-like
    The height values over which the contour is drawn.  Color-mapping is
    controlled by *cmap*, *norm*, *vmin*, and *vmax*.

levels : int or array-like, optional
    Determines the number and positions of the contour lines / regions.

    If an int *n*, use `~matplotlib.ticker.MaxNLocator`, which tries
    to automatically choose no more than *n+1* "nice" contour levels
    between minimum and maximum numeric values of *Z*.

    If array-like, draw contour lines at the specified levels.
    The values must be in increasing order.

Returns
-------
`~.contour.QuadContourSet`

Other Parameters
----------------
corner_mask : bool, default: :rc:`contour.corner_mask`
    Enable/disable corner masking, which only has an effect if *Z* is
    a masked array.  If ``False``, any quad touching a masked point is
    masked out.  If ``True``, only the triangular corners of quads
    nearest those points are always masked out, other triangular
    corners comprising three unmasked points are contoured as usual.

colors : color string or sequence of colors, optional
    The colors of the levels, i.e. the lines for `.contour` and the
    areas for `.contourf`.

    The sequence is cycled for the levels in ascending order. If the
    sequence is shorter than the number of levels, it's repeated.

    As a shortcut, single color strings may be used in place of
    one-element lists, i.e. ``'red'`` instead of ``['red']`` to color
    all levels with the same color. This shortcut does only work for
    color strings, not for other ways of specifying colors.

    By default (value *None*), the colormap specified by *cmap*
    will be used.

alpha : float, default: 1
    The alpha blending value, between 0 (transparent) and 1 (opaque).

%(cmap_doc)s

    This parameter is ignored if *colors* is set.

%(norm_doc)s

    This parameter is ignored if *colors* is set.

%(vmin_vmax_doc)s

    If *vmin* or *vmax* are not given, the default color scaling is based on
    *levels*.

    This parameter is ignored if *colors* is set.

origin : {*None*, 'upper', 'lower', 'image'}, default: None
    Determines the orientation and exact position of *Z* by specifying
    the position of ``Z[0, 0]``.  This is only relevant, if *X*, *Y*
    are not given.

    - *None*: ``Z[0, 0]`` is at X=0, Y=0 in the lower left corner.
    - 'lower': ``Z[0, 0]`` is at X=0.5, Y=0.5 in the lower left corner.
    - 'upper': ``Z[0, 0]`` is at X=N+0.5, Y=0.5 in the upper left
      corner.
    - 'image': Use the value from :rc:`image.origin`.

extent : (x0, x1, y0, y1), optional
    If *origin* is not *None*, then *extent* is interpreted as in
    `.imshow`: it gives the outer pixel boundaries. In this case, the
    position of Z[0, 0] is the center of the pixel, not a corner. If
    *origin* is *None*, then (*x0*, *y0*) is the position of Z[0, 0],
    and (*x1*, *y1*) is the position of Z[-1, -1].

    This argument is ignored if *X* and *Y* are specified in the call
    to contour.

locator : ticker.Locator subclass, optional
    The locator is used to determine the contour levels if they
    are not given explicitly via *levels*.
    Defaults to `~.ticker.MaxNLocator`.

extend : {'neither', 'both', 'min', 'max'}, default: 'neither'
    Determines the ``contourf``-coloring of values that are outside the
    *levels* range.

    If 'neither', values outside the *levels* range are not colored.
    If 'min', 'max' or 'both', color the values below, above or below
    and above the *levels* range.

    Values below ``min(levels)`` and above ``max(levels)`` are mapped
    to the under/over values of the `.Colormap`. Note that most
    colormaps do not have dedicated colors for these by default, so
    that the over and under values are the edge values of the colormap.
    You may want to set these values explicitly using
    `.Colormap.set_under` and `.Colormap.set_over`.

    .. note::

        An existing `.QuadContourSet` does not get notified if
        properties of its colormap are changed. Therefore, an explicit
        call `.QuadContourSet.changed()` is needed after modifying the
        colormap. The explicit call can be left out, if a colorbar is
        assigned to the `.QuadContourSet` because it internally calls
        `.QuadContourSet.changed()`.

    Example::

        x = np.arange(1, 10)
        y = x.reshape(-1, 1)
        h = x * y

        cs = plt.contourf(h, levels=[10, 30, 50],
            colors=['#808080', '#A0A0A0', '#C0C0C0'], extend='both')
        cs.cmap.set_over('red')
        cs.cmap.set_under('blue')
        cs.changed()

xunits, yunits : registered units, optional
    Override axis units by specifying an instance of a
    :class:`matplotlib.units.ConversionInterface`.

antialiased : bool, optional
    Enable antialiasing, overriding the defaults.  For
    filled contours, the default is *False*.  For line contours,
    it is taken from :rc:`lines.antialiased`.

nchunk : int >= 0, optional
    If 0, no subdivision of the domain.  Specify a positive integer to
    divide the domain into subdomains of *nchunk* by *nchunk* quads.
    Chunking reduces the maximum length of polygons generated by the
    contouring algorithm which reduces the rendering workload passed
    on to the backend and also requires slightly less RAM.  It can
    however introduce rendering artifacts at chunk boundaries depending
    on the backend, the *antialiased* flag and value of *alpha*.

linewidths : float or array-like, default: :rc:`contour.linewidth`
    *Only applies to* `.contour`.

    The line width of the contour lines.

    If a number, all levels will be plotted with this linewidth.

    If a sequence, the levels in ascending order will be plotted with
    the linewidths in the order specified.

    If None, this falls back to :rc:`lines.linewidth`.

linestyles : {*None*, 'solid', 'dashed', 'dashdot', 'dotted'}, optional
    *Only applies to* `.contour`.

    If *linestyles* is *None*, the default is 'solid' unless the lines are
    monochrome. In that case, negative contours will instead take their
    linestyle from the *negative_linestyles* argument.

    *linestyles* can also be an iterable of the above strings specifying a set
    of linestyles to be used. If this iterable is shorter than the number of
    contour levels it will be repeated as necessary.

negative_linestyles : {*None*, 'solid', 'dashed', 'dashdot', 'dotted'}, \
                       optional
    *Only applies to* `.contour`.

    If *linestyles* is *None* and the lines are monochrome, this argument
    specifies the line style for negative contours.

    If *negative_linestyles* is *None*, the default is taken from
    :rc:`contour.negative_linestyles`.

    *negative_linestyles* can also be an iterable of the above strings
    specifying a set of linestyles to be used. If this iterable is shorter than
    the number of contour levels it will be repeated as necessary.

hatches : list[str], optional
    *Only applies to* `.contourf`.

    A list of cross hatch patterns to use on the filled areas.
    If None, no hatching will be added to the contour.
    Hatching is supported in the PostScript, PDF, SVG and Agg
    backends only.

algorithm : {'mpl2005', 'mpl2014', 'serial', 'threaded'}, optional
    Which contouring algorithm to use to calculate the contour lines and
    polygons. The algorithms are implemented in
    `ContourPy <https://github.com/contourpy/contourpy>`_, consult the
    `ContourPy documentation <https://contourpy.readthedocs.io>`_ for
    further information.

    The default is taken from :rc:`contour.algorithm`.

clip_path : `~matplotlib.patches.Patch` or `.Path` or `.TransformedPath`
    Set the clip path.  See `~matplotlib.artist.Artist.set_clip_path`.

    .. versionadded:: 3.8

data : indexable object, optional
    DATA_PARAMETER_PLACEHOLDER

Notes
-----
1. `.contourf` differs from the MATLAB version in that it does not draw
   the polygon edges. To draw edges, add line contours with calls to
   `.contour`.

2. `.contourf` fills intervals that are closed at the top; that is, for
   boundaries *z1* and *z2*, the filled region is::

      z1 < Z <= z2

   except for the lowest interval, which is closed on both sides (i.e.
   it includes the lowest value).

3. `.contour` and `.contourf` use a `marching squares
   <https://en.wikipedia.org/wiki/Marching_squares>`_ algorithm to
   compute contour locations.  More information can be found in
   `ContourPy documentation <https://contourpy.readthedocs.io>`_.
""" % _docstring.interpd.params)
