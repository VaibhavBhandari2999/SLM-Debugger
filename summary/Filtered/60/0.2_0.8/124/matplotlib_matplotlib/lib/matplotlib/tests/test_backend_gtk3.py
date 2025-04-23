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
        
        This function sends a key event to the given widget based on the key and modifier combination provided in the list. The function iterates over a list of key-modifier pairs and sends each key event to the widget.
        
        Parameters:
        event (object): The event object containing the key and modifier information.
        
        Returns:
        None: This function does not return any value. It sends key events to the widget.
        
        Key Parameters:
        - key (int):
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
        Close a figure.
        
        This function processes a sequence of key events to determine if a figure should be closed. It appends each key event to a buffer and checks if the buffer matches a predefined sequence of key events. If the buffer matches the sequence, the function closes the current figure.
        
        Parameters:
        event (str): The key event to be processed.
        
        Returns:
        None: This function does not return any value. It closes the current figure if the key sequence matches the predefined sequence.
        
        Example:
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
