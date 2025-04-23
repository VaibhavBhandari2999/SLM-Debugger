import sys
import warnings
from contextlib import contextmanager
from typing import Generator
from typing import Optional
from typing import TYPE_CHECKING

import pytest
from _pytest.config import apply_warning_filters
from _pytest.config import Config
from _pytest.config import parse_warning_filter
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.terminal import TerminalReporter

if TYPE_CHECKING:
    from typing_extensions import Literal


def pytest_configure(config: Config) -> None:
    """
    Configure pytest to add a custom marker for filtering warnings.
    
    This function is called by pytest during its configuration phase. It adds a new marker to the test suite that can be used to filter specific warnings for a given test.
    
    Parameters:
    config (Config): The pytest configuration object.
    
    Returns:
    None: This function does not return any value. It modifies the pytest configuration in place.
    """

    config.addinivalue_line(
        "markers",
        "filterwarnings(warning): add a warning filter to the given test. "
        "see https://docs.pytest.org/en/stable/warnings.html#pytest-mark-filterwarnings ",
    )


@contextmanager
def catch_warnings_for_item(
    config: Config,
    ihook,
    when: "Literal['config', 'collect', 'runtest']",
    item: Optional[Item],
) -> Generator[None, None, None]:
    """Context manager that catches warnings generated in the contained execution block.

    ``item`` can be None if we are not in the context of an item execution.

    Each warning captured triggers the ``pytest_warning_recorded`` hook.
    """
    config_filters = config.getini("filterwarnings")
    cmdline_filters = config.known_args_namespace.pythonwarnings or []
    with warnings.catch_warnings(record=True) as log:
        # mypy can't infer that record=True means log is not None; help it.
        assert log is not None

        if not sys.warnoptions:
            # If user is not explicitly configuring warning filters, show deprecation warnings by default (#2908).
            warnings.filterwarnings("always", category=DeprecationWarning)
            warnings.filterwarnings("always", category=PendingDeprecationWarning)

        apply_warning_filters(config_filters, cmdline_filters)

        # apply filters from "filterwarnings" marks
        nodeid = "" if item is None else item.nodeid
        if item is not None:
            for mark in item.iter_markers(name="filterwarnings"):
                for arg in mark.args:
                    warnings.filterwarnings(*parse_warning_filter(arg, escape=False))

        yield

        for warning_message in log:
            ihook.pytest_warning_captured.call_historic(
                kwargs=dict(
                    warning_message=warning_message,
                    when=when,
                    item=item,
                    location=None,
                )
            )
            ihook.pytest_warning_recorded.call_historic(
                kwargs=dict(
                    warning_message=warning_message,
                    nodeid=nodeid,
                    when=when,
                    location=None,
                )
            )


def warning_record_to_str(warning_message: warnings.WarningMessage) -> str:
    """Convert a warnings.WarningMessage to a string."""
    warn_msg = warning_message.message
    msg = warnings.formatwarning(
        str(warn_msg),
        warning_message.category,
        warning_message.filename,
        warning_message.lineno,
        warning_message.line,
    )
    return msg


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: Item) -> Generator[None, None, None]:
    with catch_warnings_for_item(
        config=item.config, ihook=item.ihook, when="runtest", item=item
    ):
        yield


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection(session: Session) -> Generator[None, None, None]:
    config = session.config
    with catch_warnings_for_item(
        config=config, ihook=config.hook, when="collect", item=None
    ):
        yield


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
) -> Generator[None, None, None]:
    config = terminalreporter.config
    with catch_warnings_for_item(
        config=config, ihook=config.hook, when="config", item=None
    ):
        yield


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session: Session) -> Generator[None, None, None]:
    """
    Finish the pytest session.
    
    This function is called at the end of the pytest session. It handles the cleanup and finalization tasks for the session. The function takes a `Session` object as input and yields control back to pytest after performing necessary actions.
    
    Parameters:
    session (Session): The pytest session object.
    
    Yields:
    Generator[None, None, None]: A generator that yields control back to pytest after session cleanup.
    """

    config = session.config
    with catch_warnings_for_item(
        config=config, ihook=config.hook, when="config", item=None
    ):
        yield


@pytest.hookimpl(hookwrapper=True)
def pytest_load_initial_conftests(
    """
    Load initial pytest configuration.
    
    This function is responsible for loading the initial configuration for pytest. It uses a context manager to handle warnings during the configuration process. The function yields control back to the pytest framework after the configuration is loaded.
    
    Parameters:
    early_config (Config): The pytest configuration object to be loaded.
    
    Yields:
    None: Control is yielded back to the pytest framework after configuration is loaded.
    
    Note:
    The function uses a context manager to manage warnings during the configuration process. This is done
    """

    early_config: "Config",
) -> Generator[None, None, None]:
    with catch_warnings_for_item(
        config=early_config, ihook=early_config.hook, when="config", item=None
    ):
        yield
