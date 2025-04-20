from contextlib import nullcontext

from .. import _api
from . import backend_cairo, backend_gtk3
from .backend_gtk3 import Gtk, _BackendGTK3


@_api.deprecated("3.6")
class RendererGTK3Cairo(backend_cairo.RendererCairo):
    def set_context(self, ctx):
        self.gc.ctx = backend_cairo._to_context(ctx)


class FigureCanvasGTK3Cairo(backend_gtk3.FigureCanvasGTK3,
                            backend_cairo.FigureCanvasCairo):

    def on_draw_event(self, widget, ctx):
        """
        Draw the figure.
        
        This function is called by GTK when a draw event occurs on the figure widget.
        
        Parameters:
        widget (Gtk.Widget): The widget that received the draw event.
        ctx (cairo.Context): The Cairo context for rendering the widget.
        
        Returns:
        None: This function does not return any value. It is responsible for rendering the figure using the provided Cairo context.
        
        Notes:
        - The function uses a context manager to handle drawing with a wait cursor if the toolbar is present.
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
