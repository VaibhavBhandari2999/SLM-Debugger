import sys

import numpy as np

from . import _backend_tk
from .backend_cairo import cairo, FigureCanvasCairo
from ._backend_tk import _BackendTk, FigureCanvasTk


class FigureCanvasTkCairo(FigureCanvasCairo, FigureCanvasTk):
    def draw(self):
        """
        Draws the current figure to an image surface and updates the Tkinter photo image.
        
        This method creates a Cairo surface to draw the figure, sets the rendering context with the figure's DPI, and then draws the figure. The resulting image is then reshaped into a NumPy array and used to update a Tkinter photo image.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - No explicit parameters are passed to this method.
        
        Keywords:
        - No additional keyword arguments are accepted
        """

        width = int(self.figure.bbox.width)
        height = int(self.figure.bbox.height)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self._renderer.set_context(cairo.Context(surface))
        self._renderer.dpi = self.figure.dpi
        self.figure.draw(self._renderer)
        buf = np.reshape(surface.get_data(), (height, width, 4))
        _backend_tk.blit(
            self._tkphoto, buf,
            (2, 1, 0, 3) if sys.byteorder == "little" else (1, 2, 3, 0))


@_BackendTk.export
class _BackendTkCairo(_BackendTk):
    FigureCanvas = FigureCanvasTkCairo
