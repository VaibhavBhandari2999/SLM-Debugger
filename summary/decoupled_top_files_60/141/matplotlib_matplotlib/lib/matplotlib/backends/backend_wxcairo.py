import wx.lib.wxcairo as wxcairo

from .backend_cairo import cairo, FigureCanvasCairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from .backend_wx import (  # noqa: F401 # pylint: disable=W0611
    NavigationToolbar2Wx as NavigationToolbar2WxCairo)


class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    def draw(self, drawDC=None):
        """
        Draws the figure on a wxPython bitmap.
        
        This method renders the figure using Cairo and then converts the resulting surface to a wxPython bitmap. The bitmap is used for displaying the figure in a wxPython application.
        
        Parameters:
        drawDC (wx.DC, optional): The device context to use for drawing. If not provided, the default device context is used.
        
        Returns:
        None: This method does not return anything. It updates the internal bitmap and triggers a repaint of the associated GUI element
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
