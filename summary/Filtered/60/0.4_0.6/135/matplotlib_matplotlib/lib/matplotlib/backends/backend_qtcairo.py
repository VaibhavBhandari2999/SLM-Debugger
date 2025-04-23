import ctypes

from .backend_cairo import cairo, FigureCanvasCairo
from .backend_qt import QtCore, QtGui, _BackendQT, FigureCanvasQT
from .qt_compat import QT_API, _enum


class FigureCanvasQTCairo(FigureCanvasCairo, FigureCanvasQT):
    def draw(self):
        """
        Draw the figure.
        
        This method is called to update the figure canvas. It first checks if the `_renderer.gc.ctx` attribute exists. If it does, it sets the DPI (dots per inch) of the renderer to the figure's DPI and then draws the figure using the renderer. Finally, it calls the superclass's `draw` method.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        """

        if hasattr(self._renderer.gc, "ctx"):
            self._renderer.dpi = self.figure.dpi
            self.figure.draw(self._renderer)
        super().draw()

    def paintEvent(self, event):
        """
        Paint the widget using the provided event. This method is responsible for rendering the figure into a QImage and then drawing it on the widget.
        
        Parameters:
        - event (QPaintEvent): The paint event that triggered this method.
        
        Key Attributes:
        - device_pixel_ratio (float): The ratio used to scale the widget's dimensions to device pixels.
        - width (int): The width of the widget.
        - height (int): The height of the widget.
        - _renderer (object): The renderer used for drawing
        """

        width = int(self.device_pixel_ratio * self.width())
        height = int(self.device_pixel_ratio * self.height())
        if (width, height) != self._renderer.get_canvas_width_height():
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            self._renderer.set_context(cairo.Context(surface))
            self._renderer.dpi = self.figure.dpi
            self.figure.draw(self._renderer)
        buf = self._renderer.gc.ctx.get_target().get_data()
        if QT_API == "PyQt6":
            from PyQt6 import sip
            ptr = int(sip.voidptr(buf))
        else:
            ptr = buf
        qimage = QtGui.QImage(
            ptr, width, height,
            _enum("QtGui.QImage.Format").Format_ARGB32_Premultiplied)
        # Adjust the buf reference count to work around a memory leak bug in
        # QImage under PySide.
        if QT_API == "PySide2" and QtCore.__version_info__ < (5, 12):
            ctypes.c_long.from_address(id(buf)).value = 1
        qimage.setDevicePixelRatio(self.device_pixel_ratio)
        painter = QtGui.QPainter(self)
        painter.eraseRect(event.rect())
        painter.drawImage(0, 0, qimage)
        self._draw_rect_callback(painter)
        painter.end()


@_BackendQT.export
class _BackendQTCairo(_BackendQT):
    FigureCanvas = FigureCanvasQTCairo
