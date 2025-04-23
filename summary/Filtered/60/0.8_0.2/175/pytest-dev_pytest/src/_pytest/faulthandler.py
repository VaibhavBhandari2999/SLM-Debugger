import io
import os
import sys

import pytest


def pytest_addoption(parser):
    """
    Add an option to the pytest command-line parser to enable the faulthandler module to dump the traceback of all threads if a test takes more than a specified timeout to finish. This feature is not available on Windows.
    
    Parameters:
    - parser: The pytest command-line parser object to which the new option will be added.
    
    Key Parameters:
    - `faulthandler_timeout`: The timeout in seconds after which the traceback of all threads will be dumped. Default is 0.0 (disabled).
    
    Notes
    """

    help = (
        "Dump the traceback of all threads if a test takes "
        "more than TIMEOUT seconds to finish.\n"
        "Not available on Windows."
    )
    parser.addini("faulthandler_timeout", help, default=0.0)


def pytest_configure(config):
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
