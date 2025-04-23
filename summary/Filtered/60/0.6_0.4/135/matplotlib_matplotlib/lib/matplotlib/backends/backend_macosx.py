import os

import matplotlib as mpl
from matplotlib import _api, cbook
from matplotlib._pylab_helpers import Gcf
from . import _macosx
from .backend_agg import FigureCanvasAgg
from matplotlib.backend_bases import (
    _Backend, FigureCanvasBase, FigureManagerBase, NavigationToolbar2,
    ResizeEvent, TimerBase)
from matplotlib.figure import Figure
from matplotlib.widgets import SubplotTool


class TimerMac(_macosx.Timer, TimerBase):
    """Subclass of `.TimerBase` using CFRunLoop timer events."""
    # completely implemented at the C-level (in _macosx.Timer)


class FigureCanvasMac(FigureCanvasAgg, _macosx.FigureCanvas, FigureCanvasBase):
    # docstring inherited

    # Ideally this class would be `class FCMacAgg(FCAgg, FCMac)`
    # (FC=FigureCanvas) where FCMac would be an ObjC-implemented mac-specific
    # class also inheriting from FCBase (this is the approach with other GUI
    # toolkits).  However, writing an extension type inheriting from a Python
    # base class is slightly tricky (the extension type must be a heap type),
    # and we can just as well lift the FCBase base up one level, keeping it *at
    # the end* to have the right method resolution order.

    # Events such as button presses, mouse movements, and key presses are
    # handled in C and events (MouseEvent, etc.) are triggered from there.

    required_interactive_framework = "macosx"
    _timer_cls = TimerMac
    manager_class = _api.classproperty(lambda cls: FigureManagerMac)

    def __init__(self, figure):
        super().__init__(figure=figure)
        self._draw_pending = False
        self._is_drawing = False

    def draw(self):
        """Render the figure and update the macosx canvas."""
        # The renderer draw is done here; delaying causes problems with code
        # that uses the result of the draw() to update plot elements.
        if self._is_drawing:
            return
        with cbook._setattr_cm(self, _is_drawing=True):
            super().draw()
        self.update()

    def draw_idle(self):
        # docstring inherited
        if not (getattr(self, '_draw_pending', False) or
                getattr(self, '_is_drawing', False)):
            self._draw_pending = True
            # Add a singleshot timer to the eventloop that will call back
            # into the Python method _draw_idle to take care of the draw
            self._single_shot_timer(self._draw_idle)

    def _single_shot_timer(self, callback):
        """Add a single shot timer with the given callback"""
        # We need to explicitly stop (called from delete) the timer after
        # firing, otherwise segfaults will occur when trying to deallocate
        # the singleshot timers.
        def callback_func(callback, timer):
            callback()
            del timer
        timer = self.new_timer(interval=0)
        timer.add_callback(callback_func, callback, timer)
        timer.start()

    def _draw_idle(self):
        """
        Draw method for singleshot timer

        This draw method can be added to a singleshot timer, which can
        accumulate draws while the eventloop is spinning. This method will
        then only draw the first time and short-circuit the others.
        """
        with self._idle_draw_cntx():
            if not self._draw_pending:
                # Short-circuit because our draw request has already been
                # taken care of
                return
            self._draw_pending = False
            self.draw()

    def blit(self, bbox=None):
        """
        Blit the current state of the object to the display.
        
        Args:
        bbox (tuple, optional): A bounding box defining the region to blit. If not provided, the entire object will be blitted.
        
        Returns:
        None: This method does not return any value. It updates the display in place.
        """

        # docstring inherited
        super().blit(bbox)
        self.update()

    def resize(self, width, height):
        # Size from macOS is logical pixels, dpi is physical.
        scale = self.figure.dpi / self.device_pixel_ratio
        width /= scale
        height /= scale
        self.figure.set_size_inches(width, height, forward=False)
        ResizeEvent("resize_event", self)._process()
        self.draw_idle()


class NavigationToolbar2Mac(_macosx.NavigationToolbar2, NavigationToolbar2):

    def __init__(self, canvas):
        """
        Initializes a custom navigation toolbar for a given canvas.
        
        This method sets up a navigation toolbar for a matplotlib canvas. It loads images from a specified data path and initializes the toolbar with these images and their corresponding tooltips. The toolbar is initialized with a list of image filenames and tooltips, and it also calls the superclass initialization methods.
        
        Parameters:
        canvas (matplotlib.figure.FigureCanvasBase): The canvas for which the toolbar is being initialized.
        
        Returns:
        None: This method does not return any value.
        """

        data_path = cbook._get_data_path('images')
        _, tooltips, image_names, _ = zip(*NavigationToolbar2.toolitems)
        _macosx.NavigationToolbar2.__init__(
            self, canvas,
            tuple(str(data_path / image_name) + ".pdf"
                  for image_name in image_names if image_name is not None),
            tuple(tooltip for tooltip in tooltips if tooltip is not None))
        NavigationToolbar2.__init__(self, canvas)

    def draw_rubberband(self, event, x0, y0, x1, y1):
        self.canvas.set_rubberband(int(x0), int(y0), int(x1), int(y1))

    def remove_rubberband(self):
        self.canvas.remove_rubberband()

    def save_figure(self, *args):
        directory = os.path.expanduser(mpl.rcParams['savefig.directory'])
        filename = _macosx.choose_save_file('Save the figure',
                                            directory,
                                            self.canvas.get_default_filename())
        if filename is None:  # Cancel
            return
        # Save dir for next time, unless empty str (which means use cwd).
        if mpl.rcParams['savefig.directory']:
            mpl.rcParams['savefig.directory'] = os.path.dirname(filename)
        self.canvas.figure.savefig(filename)

    @_api.deprecated("3.6", alternative='configure_subplots()')
    def prepare_configure_subplots(self):
        """
        Prepare and configure subplots for a figure.
        
        This function creates a new figure with specified dimensions and adjusts the subplot layout. It also initializes a subplot tool and returns a canvas for the figure.
        
        Parameters:
        None
        
        Returns:
        FigureCanvasMac: A canvas for the configured figure.
        
        Notes:
        - The figure is created with a size of 6x3 inches.
        - The subplot layout is adjusted to have a top margin of 0.9.
        - A reference to the Sub
        """

        toolfig = Figure(figsize=(6, 3))
        canvas = FigureCanvasMac(toolfig)
        toolfig.subplots_adjust(top=0.9)
        # Need to keep a reference to the tool.
        _tool = SubplotTool(self.canvas.figure, toolfig)
        return canvas


class FigureManagerMac(_macosx.FigureManager, FigureManagerBase):
    _toolbar2_class = NavigationToolbar2Mac

    def __init__(self, canvas, num):
        self._shown = False
        _macosx.FigureManager.__init__(self, canvas)
        icon_path = str(cbook._get_data_path('images/matplotlib.pdf'))
        _macosx.FigureManager.set_icon(icon_path)
        FigureManagerBase.__init__(self, canvas, num)
        if self.toolbar is not None:
            self.toolbar.update()
        if mpl.is_interactive():
            self.show()
            self.canvas.draw_idle()

    def _close_button_pressed(self):
        Gcf.destroy(self)
        self.canvas.flush_events()

    @_api.deprecated("3.6")
    def close(self):
        return self._close_button_pressed()

    @classmethod
    def start_main_loop(cls):
        _macosx.show()

    def show(self):
        """
        Shows the figure if it is not already shown. If the 'figure.raise_window' parameter in the matplotlib configuration is set to True, the function will raise the window to the foreground.
        
        Parameters:
        None
        
        Returns:
        None
        """

        if not self._shown:
            self._show()
            self._shown = True
        if mpl.rcParams["figure.raise_window"]:
            self._raise()


@_Backend.export
class _BackendMac(_Backend):
    FigureCanvas = FigureCanvasMac
    FigureManager = FigureManagerMac
    mainloop = FigureManagerMac.start_main_loop
elf._raise()


@_Backend.export
class _BackendMac(_Backend):
    FigureCanvas = FigureCanvasMac
    FigureManager = FigureManagerMac
    mainloop = FigureManagerMac.start_main_loop
