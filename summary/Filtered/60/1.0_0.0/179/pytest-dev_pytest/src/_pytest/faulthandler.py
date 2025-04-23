import io
import os
import sys
from typing import Generator
from typing import TextIO

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item
from _pytest.store import StoreKey


fault_handler_stderr_key = StoreKey[TextIO]()


def pytest_addoption(parser: Parser) -> None:
    help = (
        "Dump the traceback of all threads if a test takes "
        "more than TIMEOUT seconds to finish."
    )
    parser.addini("faulthandler_timeout", help, default=0.0)


def pytest_configure(config: Config) -> None:
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

    def pytest_configure(self, config: Config) -> None:
        import faulthandler

        stderr_fd_copy = os.dup(self._get_stderr_fileno())
        config._store[fault_handler_stderr_key] = open(stderr_fd_copy, "w")
        faulthandler.enable(file=config._store[fault_handler_stderr_key])

    def pytest_unconfigure(self, config: Config) -> None:
        """
        Disable the faulthandler and close the duplicate file handle installed during pytest_configure. Re-enable the faulthandler, attaching it to the default sys.stderr to capture crashes after pytest has finished, usually during garbage collection during interpreter shutdown.
        
        Parameters:
        config (Config): The pytest configuration object containing the necessary state and settings.
        
        Returns:
        None: This function does not return any value. It performs cleanup and configuration changes for the pytest environment.
        """

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
        """
        Retrieve the file descriptor for the standard error stream.
        
        This function attempts to get the file descriptor for the standard error stream. If the standard error stream is not a file or if it lacks a fileno method, the function falls back to using the file descriptor of the fallback standard error stream.
        
        Returns:
        int: The file descriptor of the standard error stream.
        
        Raises:
        None
        
        Notes:
        - If `sys.stderr` is not a file or does not have a `fileno` method
        """

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
    def pytest_runtest_protocol(self, item: Item) -> Generator[None, None, None]:
        """
        Generate a Python docstring for the provided function.
        
        This function is designed to handle the execution of test protocols in a pytest environment, with specific focus on managing timeouts and fault handling. It ensures that if a timeout is set and a stderr stream is available, a traceback is dumped to the stderr stream after the specified timeout. If no timeout is set or no stderr stream is available, the function simply yields control to the test.
        
        Parameters:
        item (Item): The pytest item representing the test being executed
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
    def pytest_enter_pdb(self) -> None:
        """Cancel any traceback dumping due to timeout before entering pdb.
        """
        import faulthandler

        faulthandler.cancel_dump_traceback_later()

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(self) -> None:
        """Cancel any traceback dumping due to an interactive exception being
        raised.
        """
        import faulthandler

        faulthandler.cancel_dump_traceback_later()
