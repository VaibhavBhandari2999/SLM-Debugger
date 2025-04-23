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
    
    This function is called by pytest during its configuration phase. It sets up the faulthandler to dump Python tracebacks in case of a fatal error. If faulthandler is already enabled, the function does nothing. Otherwise, it duplicates the standard error file descriptor and uses it to enable faulthandler, redirecting the output to a file object stored in the pytest configuration.
    
    Parameters:
    config (pytest.Config): The pytest configuration
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
    """
    Unconfigure pytest environment.
    
    This function is called at the end of the pytest run to clean up the environment. It disables the faulthandler, which is a tool for debugging Python applications. It also closes a duplicate file object that was installed during the pytest configuration phase. If such a file object exists, it re-enables the faulthandler, attaching it to the default sys.stderr. This allows the faulthandler to capture and display crash information even after pytest has finished running,
    """

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
