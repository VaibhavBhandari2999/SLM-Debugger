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
    Retrieve the application object from the backend Qt module.
    
    This function is designed to be used as a fallback mechanism for accessing the application object (`qApp`) from the backend Qt module. If the attribute `qApp` is not found in the current module, this function will attempt to retrieve it from the backend Qt module.
    
    Parameters:
    name (str): The name of the attribute to be accessed. In this case, it should always be 'qApp'.
    
    Returns:
    object: The application object
    """

    if name == 'qApp':
        return _backend_qt.qApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
