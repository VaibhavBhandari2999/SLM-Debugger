import io
import os
import sys

import pytest


def pytest_addoption(parser):
    help = (
        "Dump the traceback of all threads if a test takes "
        "more than TIMEOUT seconds to finish.\n"
        "Not available on Windows."
    )
    parser.addini("faulthandler_timeout", help, default=0.0)


def pytest_configure(config):
    """
    Configure pytest to enable faulthandler for debugging.
    
    This function is called by pytest during its configuration phase. It sets up the faulthandler module to catch and print Python stack traces in case of a timeout or when a segmentation fault occurs.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function does not return any value. It configures the faulthandler for the pytest session.
    
    Notes:
    - The function avoids enabling faulth
    """

    import faulthandler

    # avoid trying to dup sys.stderr if faulthandler is already enabled
    if faulthandler.is_enabled():
        return

    stderr_fd_copy = os.dup(_get_stderr_fileno())
    config.fault_handler_stderr = os.fdopen(stderr_fd_copy, "w")
    faulthandler.enable(file=config.fault_handler_stderr)


def _get_stderr_fileno():
    try:
        return sys.stderr.fileno()
    except (AttributeError, io.UnsupportedOperation):
        # python-xdist monkeypatches sys.stderr with an object that is not an actual file.
        # https://docs.python.org/3/library/faulthandler.html#issue-with-file-descriptors
        # This is potentially dangerous, but the best we can do.
        return sys.__stderr__.fileno()


def pytest_unconfigure(config):
    import faulthandler

    faulthandler.disable()
    # close our dup file installed during pytest_configure
    f = getattr(config, "fault_handler_stderr", None)
    if f is not None:
        # re-enable the faulthandler, attaching it to the default sys.stderr
        # so we can see crashes after pytest has finished, usually during
        # garbage collection during interpreter shutdown
        config.fault_handler_stderr.close()
        del config.fault_handler_stderr
        faulthandler.enable(file=_get_stderr_fileno())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item):
    """
    Runs the test protocol for a given pytest item. If a timeout is specified in the pytest configuration for the 'faulthandler_timeout' option, the function will initiate a fault handler to dump a traceback after the specified timeout. The function accepts a single parameter:
    
    - item: The pytest item to be tested.
    
    The function does not return any value. It uses the 'faulthandler' module to handle tracebacks and the 'item.config.fault_handler_stderr' to specify the output stream
    """

    timeout = float(item.config.getini("faulthandler_timeout") or 0.0)
    if timeout > 0:
        import faulthandler

        stderr = item.config.fault_handler_stderr
        faulthandler.dump_traceback_later(timeout, file=stderr)
        try:
            yield
        finally:
            faulthandler.cancel_dump_traceback_later()
    else:
        yield


@pytest.hookimpl(tryfirst=True)
def pytest_enter_pdb():
    """Cancel any traceback dumping due to timeout before entering pdb.
    """
    import faulthandler

    faulthandler.cancel_dump_traceback_later()


@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact():
    """Cancel any traceback dumping due to an interactive exception being
    raised.
    """
    import faulthandler

    faulthandler.cancel_dump_traceback_later()
