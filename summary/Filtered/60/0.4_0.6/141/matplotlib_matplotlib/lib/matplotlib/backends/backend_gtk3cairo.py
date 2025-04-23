from contextlib import nullcontext

from .backend_cairo import FigureCanvasCairo
from .backend_gtk3 import Gtk, FigureCanvasGTK3, _BackendGTK3


class FigureCanvasGTK3Cairo(FigureCanvasCairo, FigureCanvasGTK3):
    def on_draw_event(self, widget, ctx):
        """
        Draw the figure.
        
        This function is called by GTK when a draw event occurs on the widget.
        
        Parameters:
        widget (Gtk.Widget): The widget that received the draw event.
        ctx (cairo.Context): The Cairo graphics context for rendering.
        
        Returns:
        None: This function does not return anything. It updates the widget's drawing surface in-place.
        
        Notes:
        - The function uses a context manager to handle drawing operations.
        - It scales the physical drawing to the logical size of the widget.
        """

        with (self.toolbar._wait_cursor_for_draw_cm() if self.toolbar
              else nullcontext()):
            self._renderer.set_context(ctx)
            scale = self.device_pixel_ratio
            # Scale physical drawing to logical size.
            ctx.scale(1 / scale, 1 / scale)
            allocation = self.get_allocation()
            Gtk.render_background(
                self.get_style_context(), ctx,
                allocation.x, allocation.y,
                allocation.width, allocation.height)
            self._renderer.dpi = self.figure.dpi
            self.figure.draw(self._renderer)


@_BackendGTK3.export
class _BackendGTK3Cairo(_BackendGTK3):
    FigureCanvas = FigureCanvasGTK3Cairo
