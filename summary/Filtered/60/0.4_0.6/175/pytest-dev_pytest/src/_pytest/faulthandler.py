import io
import os
import sys

import pytest


def pytest_addoption(parser):
    """
    Adds an option to the pytest command line to enable the faulthandler module for debugging multi-threaded tests.
    
    This function is called by pytest to add a custom option. The option allows the user to specify a timeout value (in seconds) after which the traceback of all threads will be dumped if a test takes longer than this duration to complete. This feature is particularly useful for debugging multi-threaded tests where a test might hang or take an unexpectedly long time to finish.
    
    Parameters:
    - parser
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
    """
    Unconfigure pytest environment.
    
    This function is called at the end of the pytest session to clean up any resources or configurations set up during the session. It disables the faulthandler, which is a module that can be used to dump the Python traceback to stderr in case of a Python crash. Additionally, it closes a duplicate file descriptor that was set up during the pytest_configure phase and re-enables the faulthandler to attach it to the default sys.stderr for capturing crashes after pytest has finished
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
