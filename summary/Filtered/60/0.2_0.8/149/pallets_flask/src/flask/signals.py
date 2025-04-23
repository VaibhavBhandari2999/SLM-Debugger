from __future__ import annotations

import typing as t
import warnings

from blinker import Namespace

# This namespace is only for signals provided by Flask itself.
_signals = Namespace()

template_rendered = _signals.signal("template-rendered")
before_render_template = _signals.signal("before-render-template")
request_started = _signals.signal("request-started")
request_finished = _signals.signal("request-finished")
request_tearing_down = _signals.signal("request-tearing-down")
got_request_exception = _signals.signal("got-request-exception")
appcontext_tearing_down = _signals.signal("appcontext-tearing-down")
appcontext_pushed = _signals.signal("appcontext-pushed")
appcontext_popped = _signals.signal("appcontext-popped")
message_flashed = _signals.signal("message-flashed")


def __getattr__(name: str) -> t.Any:
    """
    Retrieve the 'signals_available' attribute or raise an AttributeError for other names.
    
    This function is designed to handle attribute access for the 'signals_available' attribute in a specific context. If the attribute name is 'signals_available', it issues a deprecation warning and returns `True`. For any other attribute name, it raises an `AttributeError`.
    
    Parameters:
    name (str): The name of the attribute to retrieve.
    
    Returns:
    t.Any: The value of the 'signals_available' attribute (always
    """

    if name == "signals_available":
        warnings.warn(
            "The 'signals_available' attribute is deprecated and will be removed in"
            " Flask 2.4. Signals are always available.",
            DeprecationWarning,
            stacklevel=2,
        )
        return True

    raise AttributeError(name)
