from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg", skip_on_importerror=True)
def test_correct_key():
    """
    Test the key press event handling in a Matplotlib figure canvas.
    
    This function simulates key press events on a Matplotlib figure canvas and checks if the events are correctly received and processed.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses `Gtk.test_widget_send_key` to simulate key press events.
    - It connects to the `draw_event` and `key_press_event` signals of the figure canvas.
    - The function sends a series of key press events with different
    """

    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk
    fig = plt.figure()
    buf = []

    def send(event):
        """
        Sends a key event to the specified widget.
        
        This function simulates key presses on a widget. It iterates through a list of key and modifier pairs, and for each pair, it calls `Gtk.test_widget_send_key` to send the key event.
        
        Parameters:
        event (tuple): A tuple containing the key and modifier for the key event.
        
        Returns:
        None: This function does not return any value. It sends key events to the widget.
        
        Example:
        send((Gdk.KEY
        """

        for key, mod in [
                (Gdk.KEY_a, Gdk.ModifierType.SHIFT_MASK),
                (Gdk.KEY_a, 0),
                (Gdk.KEY_a, Gdk.ModifierType.CONTROL_MASK),
                (Gdk.KEY_agrave, 0),
                (Gdk.KEY_Control_L, Gdk.ModifierType.MOD1_MASK),
                (Gdk.KEY_Alt_L, Gdk.ModifierType.CONTROL_MASK),
                (Gdk.KEY_agrave,
                 Gdk.ModifierType.CONTROL_MASK
                 | Gdk.ModifierType.MOD1_MASK
                 | Gdk.ModifierType.MOD4_MASK),
                (0xfd16, 0),   # KEY_3270_Play.
                (Gdk.KEY_BackSpace, 0),
                (Gdk.KEY_BackSpace, Gdk.ModifierType.CONTROL_MASK),
        ]:
            # This is not actually really the right API: it depends on the
            # actual keymap (e.g. on Azerty, shift+agrave -> 0).
            Gtk.test_widget_send_key(fig.canvas, key, mod)

    def receive(event):
        buf.append(event.key)
        if buf == [
                "A", "a", "ctrl+a",
                "\N{LATIN SMALL LETTER A WITH GRAVE}",
                "alt+control", "ctrl+alt",
                "ctrl+alt+super+\N{LATIN SMALL LETTER A WITH GRAVE}",
                # (No entry for KEY_3270_Play.)
                "backspace", "ctrl+backspace",
        ]:
            plt.close(fig)

    fig.canvas.mpl_connect("draw_event", send)
    fig.canvas.mpl_connect("key_press_event", receive)
    plt.show()
