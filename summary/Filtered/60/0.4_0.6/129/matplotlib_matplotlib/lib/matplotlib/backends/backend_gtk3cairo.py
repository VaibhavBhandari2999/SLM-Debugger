from contextlib import nullcontext

from .backend_cairo import (  # noqa
    FigureCanvasCairo, _RendererGTKCairo as RendererGTK3Cairo)
from .backend_gtk3 import Gtk, FigureCanvasGTK3, _BackendGTK3


class FigureCanvasGTK3Cairo(FigureCanvasCairo, FigureCanvasGTK3):
    def on_draw_event(self, widget, ctx):
        """
        Draw the figure using the provided Cairo context.
        
        This function is triggered by a draw event and is responsible for rendering the figure. It scales the physical drawing to the logical size, sets the rendering context, and draws the figure.
        
        Parameters:
        widget (Gtk.Widget): The widget that triggered the draw event.
        ctx (cairo.Context): The Cairo context to use for rendering.
        
        Returns:
        None: This function does not return any value. It updates the widget's rendering directly.
        
        Keywords:
        toolbar
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
