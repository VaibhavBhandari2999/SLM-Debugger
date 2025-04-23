from contextlib import nullcontext

from .backend_cairo import (  # noqa
    FigureCanvasCairo, _RendererGTKCairo as RendererGTK4Cairo)
from .backend_gtk4 import Gtk, FigureCanvasGTK4, _BackendGTK4


class FigureCanvasGTK4Cairo(FigureCanvasCairo, FigureCanvasGTK4):
    _context_is_scaled = True

    def on_draw_event(self, widget, ctx):
        """
        Draw the figure using the provided Cairo context.
        
        This function is triggered by a draw event and is responsible for rendering the figure on the widget. It scales the physical drawing to the logical size and sets the context for rendering. The function also handles background rendering and sets the DPI for the figure.
        
        Parameters:
        widget (Gtk.Widget): The widget that is receiving the draw event.
        ctx (cairo.Context): The Cairo context to use for rendering.
        
        Returns:
        None: This function does not return any
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


@_BackendGTK4.export
class _BackendGTK4Cairo(_BackendGTK4):
    FigureCanvas = FigureCanvasGTK4Cairo
