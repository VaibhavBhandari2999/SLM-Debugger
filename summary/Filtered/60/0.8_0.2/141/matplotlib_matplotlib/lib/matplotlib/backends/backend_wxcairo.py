import wx.lib.wxcairo as wxcairo

from .backend_cairo import cairo, FigureCanvasCairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from .backend_wx import (  # noqa: F401 # pylint: disable=W0611
    NavigationToolbar2Wx as NavigationToolbar2WxCairo)


class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    def draw(self, drawDC=None):
        """
        Draw the figure on the wxWidgets device context.
        
        This method renders the figure using Cairo and then converts it to a wxBitmap for display.
        
        Parameters:
        - drawDC (wxDC, optional): The device context to draw on. If not provided, the method will still render the figure but may not update the GUI immediately.
        
        Returns:
        - None: This method does not return any value. It updates the internal bitmap and triggers a repaint of the associated GUI element.
        
        Key Steps:
        1. Calculate the
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
