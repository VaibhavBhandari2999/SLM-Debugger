from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg")
def test_correct_key():
    """
    Test the correct key press events are sent to the widget.
    
    This function is designed to test the key press events sent to a widget in a GTK environment. It uses the `Gtk.test_widget_send_key` function to simulate key press events and the `plt.show` function to display a figure. The function connects to the `draw_event` and `key_press_event` signals of the figure's canvas to capture and verify the key press events.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key
    """

    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk
    fig = plt.figure()
    buf = []

    def send(event):
        """
        Sends a key event to the specified widget.
        
        This function simulates key presses on a widget, such as a canvas. It supports various key combinations and modifiers.
        
        Parameters:
        event (Gdk.EventKey): The key event to be sent. This includes the key pressed and any modifiers (like shift, control, alt).
        
        Key Combinations:
        - `Gdk.KEY_a` with `Gdk.ModifierType.SHIFT_MASK`
        - `Gdk.KEY_a` without any modifiers
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
        """
        Closes the current figure if the received key events match a specific sequence.
        
        Parameters:
        event (Event): The key event received.
        
        Returns:
        None: This function does not return anything. It closes the current figure if the key events match the specified sequence.
        
        Key Events Sequence:
        - 'A' or 'a': Pressing the 'A' or 'a' key.
        - 'ctrl+a': Pressing the 'A' key while holding the Ctrl key.
        - '\
        """

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
