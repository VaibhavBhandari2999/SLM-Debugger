import wx

from .backend_agg import FigureCanvasAgg
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from .backend_wx import (  # noqa: F401 # pylint: disable=W0611
    NavigationToolbar2Wx as NavigationToolbar2WxAgg)


class FigureCanvasWxAgg(FigureCanvasAgg, _FigureCanvasWxBase):
    def draw(self, drawDC=None):
        """
        Render the figure using agg.
        """
        FigureCanvasAgg.draw(self)
        self.bitmap = _rgba_to_wx_bitmap(self.get_renderer().buffer_rgba())
        self._isDrawn = True
        self.gui_repaint(drawDC=drawDC)

    def blit(self, bbox=None):
        """
        Blit the current buffer to the bitmap.
        
        This method updates the bitmap with the current buffer content. If a bounding box is provided, only the specified region is updated. The method can be used to refresh a specific area of the GUI representation.
        
        Parameters:
        bbox (tuple, optional): A tuple (x0, y0, width, height) defining the region to be updated. If not provided, the entire bitmap is updated.
        
        Returns:
        None: This method does not return any value
        """

        # docstring inherited
        bitmap = _rgba_to_wx_bitmap(self.get_renderer().buffer_rgba())
        if bbox is None:
            self.bitmap = bitmap
        else:
            srcDC = wx.MemoryDC(bitmap)
            destDC = wx.MemoryDC(self.bitmap)
            x = int(bbox.x0)
            y = int(self.bitmap.GetHeight() - bbox.y1)
            destDC.Blit(x, y, int(bbox.width), int(bbox.height), srcDC, x, y)
            destDC.SelectObject(wx.NullBitmap)
            srcDC.SelectObject(wx.NullBitmap)
        self.gui_repaint()


def _rgba_to_wx_bitmap(rgba):
    """Convert an RGBA buffer to a wx.Bitmap."""
    h, w, _ = rgba.shape
    return wx.Bitmap.FromBufferRGBA(w, h, rgba)


@_BackendWx.export
class _BackendWxAgg(_BackendWx):
    FigureCanvas = FigureCanvasWxAgg
