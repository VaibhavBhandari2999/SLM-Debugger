import wx.lib.wxcairo as wxcairo

from .backend_cairo import cairo, FigureCanvasCairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from .backend_wx import (  # noqa: F401 # pylint: disable=W0611
    NavigationToolbar2Wx as NavigationToolbar2WxCairo)


class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    def draw(self, drawDC=None):
        """
        Draws the figure on the canvas.
        
        This method renders the figure using Cairo and then converts it to a wx.Bitmap for display.
        
        Parameters:
        drawDC (wx.DC, optional): The device context to use for the repaint. If not provided, the canvas will automatically repaint itself.
        
        Returns:
        None
        
        Key Parameters:
        - drawDC: The device context for the repaint. If not provided, the canvas will automatically repaint itself.
        
        Details:
        - The method first calculates the size of
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
