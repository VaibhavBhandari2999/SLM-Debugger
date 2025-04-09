import sys
import warnings
from contextlib import contextmanager

import pytest

SHOW_PYTEST_WARNINGS_ARG = "-Walways::pytest.RemovedInPytest4Warning"


def _setoption(wmod, arg):
    """
    Copy of the warning._setoption function but does not escape arguments.
    """
    parts = arg.split(":")
    if len(parts) > 5:
        raise wmod._OptionError("too many fields (max 5): {!r}".format(arg))
    while len(parts) < 5:
        parts.append("")
    action, message, category, module, lineno = [s.strip() for s in parts]
    action = wmod._getaction(action)
    category = wmod._getcategory(category)
    if lineno:
        try:
            lineno = int(lineno)
            if lineno < 0:
                raise ValueError
        except (ValueError, OverflowError):
            raise wmod._OptionError("invalid lineno {!r}".format(lineno))
    else:
        lineno = 0
    wmod.filterwarnings(action, message, category, module, lineno)


def pytest_addoption(parser):
    """
    Summary: This function adds options to the pytest framework for handling warnings.
    
    Parameters:
    parser (argparse.ArgumentParser): The argument parser object for pytest.
    
    Returns:
    None
    
    Important Functions:
    - `addoption`: Adds an option to the argument parser.
    - `getgroup`: Retrieves a group from the argument parser.
    - `addini`: Adds an ini option to the argument parser.
    
    Usage:
    This function is typically called during the setup of a pytest test
    """

    group = parser.getgroup("pytest-warnings")
    group.addoption(
        "-W",
        "--pythonwarnings",
        action="append",
        help="set which warnings to report, see -W option of python itself.",
    )
    parser.addini(
        "filterwarnings",
        type="linelist",
        help="Each line specifies a pattern for "
        "warnings.filterwarnings. "
        "Processed after -W and --pythonwarnings.",
    )


def pytest_configure(config):
    """
    Configure pytest with a custom marker to filter warnings.
    
    This function is called by pytest during its configuration phase. It adds a new marker named 'filterwarnings' to the test suite, allowing users to specify warning filters for individual tests. The marker takes a single argument, `warning`, which is a string representing the warning category or message pattern to be filtered.
    
    Args:
    config (pytest.Config): The pytest configuration object.
    
    Example usage:
    >>> pytest_configure(config)
    >>> @pytest
    """

    config.addinivalue_line(
        "markers",
        "filterwarnings(warning): add a warning filter to the given test. "
        "see https://docs.pytest.org/en/latest/warnings.html#pytest-mark-filterwarnings ",
    )


@contextmanager
def catch_warnings_for_item(config, ihook, when, item):
    """
    Context manager that catches warnings generated in the contained execution block.

    ``item`` can be None if we are not in the context of an item execution.

    Each warning captured triggers the ``pytest_warning_captured`` hook.
    """
    cmdline_filters = config.getoption("pythonwarnings") or []
    inifilters = config.getini("filterwarnings")
    with warnings.catch_warnings(record=True) as log:

        if not sys.warnoptions:
            # if user is not explicitly configuring warning filters, show deprecation warnings by default (#2908)
            warnings.filterwarnings("always", category=DeprecationWarning)
            warnings.filterwarnings("always", category=PendingDeprecationWarning)

        warnings.filterwarnings("error", category=pytest.RemovedInPytest4Warning)
        warnings.filterwarnings("error", category=pytest.PytestDeprecationWarning)

        # filters should have this precedence: mark, cmdline options, ini
        # filters should be applied in the inverse order of precedence
        for arg in inifilters:
            _setoption(warnings, arg)

        for arg in cmdline_filters:
            warnings._setoption(arg)

        if item is not None:
            for mark in item.iter_markers(name="filterwarnings"):
                for arg in mark.args:
                    _setoption(warnings, arg)

        yield

        for warning_message in log:
            ihook.pytest_warning_captured.call_historic(
                kwargs=dict(warning_message=warning_message, when=when, item=item)
            )


def warning_record_to_str(warning_message):
    """Convert a warnings.WarningMessage to a string."""
    warn_msg = warning_message.message
    msg = warnings.formatwarning(
        warn_msg,
        warning_message.category,
        warning_message.filename,
        warning_message.lineno,
        warning_message.line,
    )
    return msg


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item):
    """
    Runs the test protocol for a given test item.
    
    This function is responsible for executing the test protocol for a specific test item. It uses the `catch_warnings_for_item` context manager to handle any warnings that may occur during the test execution. The function takes a single argument:
    
    :param item: The test item to be executed.
    
    The function does not return any value but yields control back to the caller after executing the test protocol.
    """

    with catch_warnings_for_item(
        config=item.config, ihook=item.ihook, when="runtest", item=item
    ):
        yield


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection(session):
    """
    Summary: This function is responsible for collecting test cases during the pytest run.
    
    Parameters:
    session (pytest.Session): The pytest session object containing information about the current test run.
    
    Returns:
    None
    
    Notes:
    - The function uses the `catch_warnings_for_item` context manager to handle warnings during collection.
    - It yields control to allow other hooks or plugins to collect items before proceeding.
    """

    config = session.config
    with catch_warnings_for_item(
        config=config, ihook=config.hook, when="collect", item=None
    ):
        yield


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter):
    """
    pytest_terminal_summary is a function that takes a terminalreporter object as an argument. It uses the config attribute of the terminalreporter object to access configuration settings. The function then uses the catch_warnings_for_item method from the config.hook module to handle warnings during the config phase. The function yields control back to the caller after executing the catch_warnings_for_item method.
    """

    config = terminalreporter.config
    with catch_warnings_for_item(
        config=config, ihook=config.hook, when="config", item=None
    ):
        yield


def _issue_warning_captured(warning, hook, stacklevel):
    """
    This function should be used instead of calling ``warnings.warn`` directly when we are in the "configure" stage:
    at this point the actual options might not have been set, so we manually trigger the pytest_warning_captured
    hook so we can display this warnings in the terminal. This is a hack until we can sort out #2891.

    :param warning: the warning instance.
    :param hook: the hook caller
    :param stacklevel: stacklevel forwarded to warnings.warn
    """
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", type(warning))
        warnings.warn(warning, stacklevel=stacklevel)
    hook.pytest_warning_captured.call_historic(
        kwargs=dict(warning_message=records[0], when="config", item=None)
    )
