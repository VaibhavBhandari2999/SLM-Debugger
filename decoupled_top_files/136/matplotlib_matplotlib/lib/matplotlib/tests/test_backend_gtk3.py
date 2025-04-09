from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg", skip_on_importerror=True)
def test_correct_key():
    """
    Test the correct key press events are triggered by the widget.
    
    This function connects draw_event and key_press_event handlers to a figure's canvas.
    The `send` function sends various key events with different modifiers, while the `receive` function appends received keys to a buffer.
    The test checks if the received keys match the expected sequence.
    """

    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk
    fig = plt.figure()
    buf = []

    def send(event):
        """
        Sends a key event to the specified widget.
        
        Args:
        event: The key event to be sent, which includes the key code and modifiers.
        
        Summary:
        This function sends a key event to the specified widget using the `Gtk.test_widget_send_key` method. It iterates through a list of key codes and modifiers, and for each combination, it calls `Gtk.test_widget_send_key` with the corresponding key and modifier values. The function does not return any value but affects the
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
        Receive keyboard events and close the figure when specific key sequences are detected.
        
        Args:
        event (Event): The keyboard event to be processed.
        
        Summary:
        This function appends the received key event to a buffer. If the buffer matches a predefined sequence of key events, it closes the current figure using `plt.close(fig)`.
        
        Important Functions:
        - `buf.append(event.key)`: Appends the key event to the buffer.
        - `plt.close(fig)`: Closes
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
