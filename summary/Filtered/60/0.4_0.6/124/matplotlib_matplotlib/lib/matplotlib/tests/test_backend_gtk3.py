from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg", skip_on_importerror=True)
def test_correct_key():
    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk
    fig = plt.figure()
    buf = []

    def send(event):
        """
        Sends a key event to the specified widget.
        
        This function sends a key event to the given widget based on the provided key and modifier combination. The key can be a specific key code or a Unicode character, and the modifier can be a combination of shift, control, alt, and mod1/mod4 masks.
        
        Parameters:
        event (tuple): A tuple containing the key and modifier combination to be sent. The key can be a specific key code (e.g., Gdk.KEY_a) or a
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
        Closes the current figure if the received key sequence matches a predefined list.
        
        Parameters:
        event (Event): The keyboard event containing the key pressed.
        
        Returns:
        None: This function does not return anything. It directly closes the current figure if the key sequence matches the predefined list.
        
        Key Sequence:
        The function checks if the sequence of keys in the event matches the following:
        - 'A', 'a', 'ctrl+a'
        - '\N{LATIN SMALL LETTER A WITH GRA
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
