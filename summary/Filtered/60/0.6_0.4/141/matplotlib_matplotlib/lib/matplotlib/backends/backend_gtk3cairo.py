from contextlib import nullcontext

from .backend_cairo import FigureCanvasCairo
from .backend_gtk3 import Gtk, FigureCanvasGTK3, _BackendGTK3


class FigureCanvasGTK3Cairo(FigureCanvasCairo, FigureCanvasGTK3):
    def on_draw_event(self, widget, ctx):
        """
        Draw the figure using the provided Cairo context.
        
        Parameters:
        widget (Gtk.Widget): The widget that is triggering the draw event.
        ctx (cairo.Context): The Cairo context to use for rendering.
        
        This method is called in response to a draw event. It uses the provided widget and Cairo context to render the figure. The physical drawing is scaled to the logical size, and the background is rendered before the figure is drawn. The DPI of the renderer is set to the figure's DPI, and the
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
