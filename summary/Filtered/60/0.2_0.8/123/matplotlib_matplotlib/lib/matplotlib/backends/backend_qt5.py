from .. import backends

backends._QT_FORCE_QT5_BINDING = True


from .backend_qt import (  # noqa
    backend_version, SPECIAL_KEYS,
    # Public API
    cursord, _create_qApp, _BackendQT, TimerQT, MainWindow, FigureCanvasQT,
    FigureManagerQT, ToolbarQt, NavigationToolbar2QT, SubplotToolQt,
    SaveFigureQt, ConfigureSubplotsQt, SetCursorQt, RubberbandQt,
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
    Get an attribute from the module.
    
    This function is used to retrieve attributes from the module. If the attribute name is 'qApp', it returns the qApp object from the Qt backend. For any other attribute, it raises an AttributeError.
    
    Parameters:
    name (str): The name of the attribute to retrieve.
    
    Returns:
    object: The value of the attribute if it exists.
    
    Raises:
    AttributeError: If the attribute does not exist in the module.
    """

    if name == 'qApp':
        return _backend_qt.qApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
