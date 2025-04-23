from .. import backends

backends._QT_FORCE_QT5_BINDING = True


from .backend_qt import (  # noqa
    SPECIAL_KEYS,
    # Public API
    cursord, _create_qApp, _BackendQT, TimerQT, MainWindow, FigureCanvasQT,
    FigureManagerQT, ToolbarQt, NavigationToolbar2QT, SubplotToolQt,
    SaveFigureQt, ConfigureSubplotsQt, RubberbandQt,
    HelpQt, ToolCopyToClipboardQT,
    # internal re-exports
    FigureCanvasBase,  FigureManagerBase, MouseButton, NavigationToolbar2,
    TimerBase, ToolContainerBase, figureoptions, Gcf
)
from . import backend_qt as _backend_qt  # noqa


@_BackendQT.export
class _BackendQT5(_BackendQT):
    pass


def __getattr__(name):
    """
    `__getattr__(name)`
    
    Retrieve an attribute from the module.
    
    Parameters:
    - `name` (str): The name of the attribute to retrieve.
    
    Returns:
    - The value of the attribute if it exists, otherwise raises an `AttributeError`.
    
    Notes:
    - This function is used to dynamically retrieve attributes from the module. If the attribute is 'qApp', it returns the `_backend_qt.qApp` object. For any other attribute, it raises an `AttributeError`.
    """

    if name == 'qApp':
        return _backend_qt.qApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
