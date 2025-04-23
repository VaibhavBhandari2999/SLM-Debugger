import wx.lib.wxcairo as wxcairo

from .. import _api
from .backend_cairo import cairo, FigureCanvasCairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase, FigureFrameWx
from .backend_wx import (  # noqa: F401 # pylint: disable=W0611
    NavigationToolbar2Wx as NavigationToolbar2WxCairo)


@_api.deprecated(
    "3.6", alternative="FigureFrameWx(..., canvas_class=FigureCanvasWxCairo)")
class FigureFrameWxCairo(FigureFrameWx):
    def get_canvas(self, fig):
        return FigureCanvasWxCairo(self, -1, fig)


class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    """
    The FigureCanvas contains the figure and does event handling.

    In the wxPython backend, it is derived from wxPanel, and (usually) lives
    inside a frame instantiated by a FigureManagerWx. The parent window
    probably implements a wxSizer to control the displayed control size - but
    we give a hint as to our preferred minimum size.
    """

    def draw(self, drawDC=None):
        """
        Draw the figure using Cairo and wxPython.
        
        This method renders the figure using Cairo for drawing and wxPython for displaying the bitmap. It sets the context, DPI, and draws the figure. The resulting bitmap is then assigned to the `bitmap` attribute.
        
        Parameters:
        drawDC (wx.DC, optional): The device context to use for drawing. If not provided, the default device context is used.
        
        Returns:
        None: This method does not return any value. It updates the `bitmap
        """

        size = self.figure.bbox.size.astype(int)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *size)
        self._renderer.set_context(cairo.Context(surface))
        self._renderer.dpi = self.figure.dpi
        self.figure.draw(self._renderer)
        self.bitmap = wxcairo.BitmapFromImageSurface(surface)
        self._isDrawn = True
        self.gui_repaint(drawDC=drawDC)


@_BackendWx.export
class _BackendWxCairo(_BackendWx):
    FigureCanvas = FigureCanvasWxCairo
