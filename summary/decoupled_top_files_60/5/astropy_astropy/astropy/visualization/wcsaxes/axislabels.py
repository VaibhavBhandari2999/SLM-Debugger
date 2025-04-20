# Licensed under a 3-clause BSD style license - see LICENSE.rst


import numpy as np

from matplotlib.text import Text
import matplotlib.transforms as mtransforms

from .frame import RectangularFrame


class AxisLabels(Text):

    def __init__(self, frame, minpad=1, *args, **kwargs):
        """
        Initialize a new axis object within a given frame.
        
        Parameters:
        frame (object): The frame within which the axis is to be created.
        minpad (float, optional): Minimum padding to apply. Default is 1.
        *args: Variable length argument list to be passed to the superclass initializer.
        **kwargs: Arbitrary keyword arguments to be passed to the superclass initializer.
        
        This method sets up the axis object, enabling it to be visible and positioned correctly within the frame. It also initializes
        """

        self._frame = frame
        super().__init__(*args, **kwargs)
        self.set_clip_on(True)
        self.set_visible_axes('all')
        self.set_ha('center')
        self.set_va('center')
        self._minpad = minpad
        self._visibility_rule = 'labels'

    def get_minpad(self, axis):
        """
        Get the minimum padding for a given axis.
        
        Parameters:
        axis (int): The axis for which to get the minimum padding.
        
        Returns:
        int: The minimum padding for the specified axis. If the axis is not specified, returns the default minimum padding.
        
        Raises:
        TypeError: If the provided axis is not an integer.
        
        Example:
        >>> obj = SomeClass()
        >>> obj.get_minpad(1)
        10
        >>> obj.get_minpad()
        5
        """

        try:
            return self._minpad[axis]
        except TypeError:
            return self._minpad

    def set_visible_axes(self, visible_axes):
        self._visible_axes = visible_axes

    def get_visible_axes(self):
        """
        Retrieve the visible axes for the plot.
        
        Parameters:
        self (Plotter): The instance of the Plotter class.
        
        Returns:
        list: A list of axes that are visible.
        
        Notes:
        If `_visible_axes` is set to 'all', all axes in `_frame` are returned.
        Otherwise, only the axes specified in `_visible_axes` that are present in `_frame` are returned.
        """

        if self._visible_axes == 'all':
            return self._frame.keys()
        else:
            return [x for x in self._visible_axes if x in self._frame]

    def set_minpad(self, minpad):
        self._minpad = minpad

    def set_visibility_rule(self, value):
        """
        Sets the visibility rule for axis labels and ticks.
        
        Parameters:
        value (str): The visibility rule to apply. Must be one of 'always', 'labels', or 'ticks'.
        
        Raises:
        ValueError: If the provided value is not one of the allowed options.
        
        This function updates the internal state of the object to reflect the specified visibility rule for axis labels and ticks.
        """

        allowed = ['always', 'labels', 'ticks']
        if value not in allowed:
            raise ValueError("Axis label visibility rule must be one of{}".format(' / '.join(allowed)))

        self._visibility_rule = value

    def get_visibility_rule(self):
        return self._visibility_rule

    def draw(self, renderer, bboxes, ticklabels_bbox,
             coord_ticklabels_bbox, ticks_locs, visible_ticks):

        if not self.get_visible():
            return

        text_size = renderer.points_to_pixels(self.get_size())

        for axis in self.get_visible_axes():

            # Flatten the bboxes for all coords and all axes
            ticklabels_bbox_list = []
            for bbcoord in ticklabels_bbox.values():
                for bbaxis in bbcoord.values():
                    ticklabels_bbox_list += bbaxis

            if self.get_visibility_rule() == 'ticks':
                if not ticks_locs[axis]:
                    continue

            elif self.get_visibility_rule() == 'labels':
                if not coord_ticklabels_bbox:
                    continue

            padding = text_size * self.get_minpad(axis)

            # Find position of the axis label. For now we pick the mid-point
            # along the path but in future we could allow this to be a
            # parameter.
            x_disp, y_disp = self._frame[axis].pixel[:, 0], self._frame[axis].pixel[:, 1]
            d = np.hstack([0., np.cumsum(np.sqrt(np.diff(x_disp) ** 2 + np.diff(y_disp) ** 2))])
            xcen = np.interp(d[-1] / 2., d, x_disp)
            ycen = np.interp(d[-1] / 2., d, y_disp)

            # Find segment along which the mid-point lies
            imin = np.searchsorted(d, d[-1] / 2.) - 1

            # Find normal of the axis label facing outwards on that segment
            normal_angle = self._frame[axis].normal_angle[imin] + 180.

            label_angle = (normal_angle - 90.) % 360.
            if 135 < label_angle < 225:
                label_angle += 180
            self.set_rotation(label_angle)

            # Find label position by looking at the bounding box of ticks'
            # labels and the image. It sets the default padding at 1 times the
            # axis label font size which can also be changed by setting
            # the minpad parameter.

            if isinstance(self._frame, RectangularFrame):

                if len(ticklabels_bbox_list) > 0 and ticklabels_bbox_list[0] is not None:
                    coord_ticklabels_bbox[axis] = [mtransforms.Bbox.union(ticklabels_bbox_list)]
                else:
                    coord_ticklabels_bbox[axis] = [None]

                if axis == 'l':
                    if axis in visible_ticks and coord_ticklabels_bbox[axis][0] is not None:
                        left = coord_ticklabels_bbox[axis][0].xmin
                    else:
                        left = xcen
                    xpos = left - padding
                    self.set_position((xpos, ycen))

                elif axis == 'r':
                    if axis in visible_ticks and coord_ticklabels_bbox[axis][0] is not None:
                        right = coord_ticklabels_bbox[axis][0].x1
                    else:
                        right = xcen
                    xpos = right + padding
                    self.set_position((xpos, ycen))

                elif axis == 'b':
                    if axis in visible_ticks and coord_ticklabels_bbox[axis][0] is not None:
                        bottom = coord_ticklabels_bbox[axis][0].ymin
                    else:
                        bottom = ycen
                    ypos = bottom - padding
                    self.set_position((xcen, ypos))

                elif axis == 't':
                    if axis in visible_ticks and coord_ticklabels_bbox[axis][0] is not None:
                        top = coord_ticklabels_bbox[axis][0].y1
                    else:
                        top = ycen
                    ypos = top + padding
                    self.set_position((xcen, ypos))

            else:  # arbitrary axis

                dx = np.cos(np.radians(normal_angle)) * (padding + text_size * 1.5)
                dy = np.sin(np.radians(normal_angle)) * (padding + text_size * 1.5)

                self.set_position((xcen + dx, ycen + dy))

            super().draw(renderer)

            bb = super().get_window_extent(renderer)
            bboxes.append(bb)
