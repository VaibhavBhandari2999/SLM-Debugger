from matplotlib import pyplot as plt

import pytest


pytest.importorskip("matplotlib.backends.backend_gtk3agg")


@pytest.mark.backend("gtk3agg", skip_on_importerror=True)
def test_correct_key():
    """
    Test the correct key press events are sent to the canvas.
    
    This function is designed to test the key press events in a matplotlib figure canvas.
    It sends various key press events and checks if the correct keys are received.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    This function uses the `pytest.xfail` decorator to mark the test as expected to fail.
    The test is expected to fail because the `test_widget_send_event` method is not triggering the `key_press_event`.
    """

    pytest.xfail("test_widget_send_event is not triggering key_press_event")

    from gi.repository import Gdk, Gtk
    fig = plt.figure()
    buf = []

    def send(event):
        """
        Sends a key event to the specified widget.
        
        This function sends a key event to the given widget, `fig.canvas`, based on the provided key and modifier combination. The function iterates over a list of key-modifier pairs and sends each key event to the widget.
        
        Parameters:
        event (tuple): A tuple containing the key and modifier combination to be sent to the widget. The key can be a specific key code or 0 for any key, and the modifier is a bitmask representing the
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
