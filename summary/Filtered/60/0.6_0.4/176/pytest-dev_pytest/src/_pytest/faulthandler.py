import io
import os
import sys
from typing import TextIO

import pytest
from _pytest.store import StoreKey


fault_handler_stderr_key = StoreKey[TextIO]()


def pytest_addoption(parser):
    """
    This function is used to add an option to the pytest configuration. It configures the pytest framework to dump the traceback of all threads if a test takes more than a specified timeout (in seconds) to complete. The function accepts a `parser` object as an argument, which is used to define the option. The option is defined using the `addini` method of the `parser` object. The `faulthandler_timeout` option is described as a timeout value in seconds, with a
    """

    help = (
        "Dump the traceback of all threads if a test takes "
        "more than TIMEOUT seconds to finish."
    )
    parser.addini("faulthandler_timeout", help, default=0.0)


def pytest_configure(config):
    import faulthandler

    if not faulthandler.is_enabled():
        # faulthhandler is not enabled, so install plugin that does the actual work
        # of enabling faulthandler before each test executes.
        config.pluginmanager.register(FaultHandlerHooks(), "faulthandler-hooks")
    else:
        from _pytest.warnings import _issue_warning_captured

        # Do not handle dumping to stderr if faulthandler is already enabled, so warn
        # users that the option is being ignored.
        timeout = FaultHandlerHooks.get_timeout_config_value(config)
        if timeout > 0:
            _issue_warning_captured(
                pytest.PytestConfigWarning(
                    "faulthandler module enabled before pytest configuration step, "
                    "'faulthandler_timeout' option ignored"
                ),
                config.hook,
                stacklevel=2,
            )


class FaultHandlerHooks:
    """Implements hooks that will actually install fault handler before tests execute,
    as well as correctly handle pdb and internal errors."""

    def pytest_configure(self, config):
        """
        Configure pytest environment for fault handler.
        
        This function is called during the pytest configuration phase. It sets up the fault handler to capture and log unhandled exceptions.
        
        Parameters:
        config (pytest.Config): The pytest configuration object.
        
        Returns:
        None: This function does not return any value. It configures the fault handler for the pytest session.
        
        Key Details:
        - The function uses `faulthandler` to enable fault handling.
        - It duplicates the standard error file descriptor and opens a new file for
        """

        import faulthandler

        stderr_fd_copy = os.dup(self._get_stderr_fileno())
        config._store[fault_handler_stderr_key] = open(stderr_fd_copy, "w")
        faulthandler.enable(file=config._store[fault_handler_stderr_key])

    def pytest_unconfigure(self, config):
        import faulthandler

        faulthandler.disable()
        # close our dup file installed during pytest_configure
        # re-enable the faulthandler, attaching it to the default sys.stderr
        # so we can see crashes after pytest has finished, usually during
        # garbage collection during interpreter shutdown
        config._store[fault_handler_stderr_key].close()
        del config._store[fault_handler_stderr_key]
        faulthandler.enable(file=self._get_stderr_fileno())

    @staticmethod
    def _get_stderr_fileno():
        try:
            return sys.stderr.fileno()
        except (AttributeError, io.UnsupportedOperation):
            # pytest-xdist monkeypatches sys.stderr with an object that is not an actual file.
            # https://docs.python.org/3/library/faulthandler.html#issue-with-file-descriptors
            # This is potentially dangerous, but the best we can do.
            return sys.__stderr__.fileno()

    @staticmethod
    def get_timeout_config_value(config):
        return float(config.getini("faulthandler_timeout") or 0.0)

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_protocol(self, item):
        """
        Runs the test protocol for a given test item.
        
        This function is responsible for handling test timeouts and dumping stack traces if an error occurs. It takes a test item as input and manages the timeout configuration and stderr redirection for fault handling.
        
        Parameters:
        item (pytest.Item): The test item to be executed.
        
        Returns:
        None: This function does not return a value. It yields control to the test execution.
        
        Key Parameters:
        - `item`: The test item to be executed. This is a
        """

        timeout = self.get_timeout_config_value(item.config)
        stderr = item.config._store[fault_handler_stderr_key]
        if timeout > 0 and stderr is not None:
            import faulthandler

            faulthandler.dump_traceback_later(timeout, file=stderr)
            try:
                yield
            finally:
                faulthandler.cancel_dump_traceback_later()
        else:
            yield

    @pytest.hookimpl(tryfirst=True)
    def pytest_enter_pdb(self):
        """Cancel any traceback dumping due to timeout before entering pdb.
        """
        import faulthandler

        faulthandler.cancel_dump_traceback_later()

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(self):
        """Cancel any traceback dumping due to an interactive exception being
        raised.
        """
        import faulthandler

        faulthandler.cancel_dump_traceback_later()
