import ctypes

from .backend_cairo import cairo, FigureCanvasCairo
from .backend_qt import QtCore, QtGui, _BackendQT, FigureCanvasQT
from .qt_compat import QT_API, _enum, _setDevicePixelRatio


class FigureCanvasQTCairo(FigureCanvasCairo, FigureCanvasQT):
    def draw(self):
        if hasattr(self._renderer.gc, "ctx"):
            self._renderer.dpi = self.figure.dpi
            self.figure.draw(self._renderer)
        super().draw()

    def paintEvent(self, event):
        """
        Paint event handler for the widget.
        
        This method is responsible for rendering the figure to the widget during a paint event. It calculates the appropriate dimensions and updates the canvas size if necessary. The figure is then drawn using the Cairo renderer, and the resulting image is converted to a QImage for display.
        
        Parameters:
        event (QPaintEvent): The paint event object.
        
        Key Parameters:
        - device_pixel_ratio (float): The ratio between device pixels and logical pixels.
        - width (int): The width
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
        if QT_API in ('PySide', 'PySide2'):
            if QtCore.__version_info__ < (5, 12):
                ctypes.c_long.from_address(id(buf)).value = 1
        _setDevicePixelRatio(qimage, self.device_pixel_ratio)
        painter = QtGui.QPainter(self)
        painter.eraseRect(event.rect())
        painter.drawImage(0, 0, qimage)
        self._draw_rect_callback(painter)
        painter.end()


@_BackendQT.export
class _BackendQTCairo(_BackendQT):
    FigureCanvas = FigureCanvasQTCairo
