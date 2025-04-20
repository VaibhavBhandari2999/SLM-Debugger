from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg", skip_on_importerror=True)
def test_correct_key():
    """
    Test the correct key press events are sent to the canvas.
    
    This function is designed to test the key press events sent to a matplotlib
    figure canvas. It uses GTK's `Gtk.test_widget_send_key` to simulate key
    presses and `mpl_connect` to capture and verify the events.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `pytest.xfail` to mark the test as expected to fail.
    - It simulates key presses on a matplotlib
    """

    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk  # type: ignore
    fig = plt.figure()
    buf = []

    def send(event):
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
        
        This function processes keyboard events to determine if a figure should be closed. It appends the received key event to a buffer and checks if the buffer matches a specific sequence of key events.
        
        Parameters:
        event (Event): The keyboard event received.
        
        Returns:
        None: This function does not return any value. It closes the figure if the buffer matches a specific sequence of key events.
        
        Example:
        >>> receive(event)
        # If the buffer matches the specified sequence, the current
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
