from contextlib import nullcontext

from .. import _api
from . import backend_cairo, backend_gtk4
from .backend_gtk4 import Gtk, _BackendGTK4


@_api.deprecated("3.6")
class RendererGTK4Cairo(backend_cairo.RendererCairo):
    def set_context(self, ctx):
        self.gc.ctx = backend_cairo._to_context(ctx)


class FigureCanvasGTK4Cairo(backend_gtk4.FigureCanvasGTK4,
                            backend_cairo.FigureCanvasCairo):
    _context_is_scaled = True

    def on_draw_event(self, widget, ctx):
        """
        Draw the figure using the provided Cairo context.
        
        This function is responsible for rendering the figure on the screen. It scales the physical drawing to the logical size and sets the DPI for rendering. The function also handles background rendering and ensures that the figure is drawn correctly.
        
        Parameters:
        widget (Gtk.Widget): The widget that is handling the draw event.
        ctx (cairo.Context): The Cairo context to use for rendering.
        
        Returns:
        None: This function does not return any value. It modifies the rendering
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
