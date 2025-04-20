from typing import List
from typing import Optional
from typing import TYPE_CHECKING

import pytest
from _pytest import nodes
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.reports import TestReport

if TYPE_CHECKING:
    from _pytest.cacheprovider import Cache

STEPWISE_CACHE_DIR = "cache/stepwise"


def pytest_addoption(parser: Parser) -> None:
    """
    Add options to the pytest command line.
    
    This function is responsible for adding options to the pytest command line interface. It specifically adds two options:
    - `--sw` or `--stepwise`: If set, the pytest will exit on the first test failure and continue from the last failing test on subsequent runs.
    - `--sw-skip` or `--stepwise-skip`: If set, the pytest will ignore the first failing test but stop on the next failing test. This option implicitly enables
    """

    group = parser.getgroup("general")
    group.addoption(
        "--sw",
        "--stepwise",
        action="store_true",
        default=False,
        dest="stepwise",
        help="Exit on test failure and continue from last failing test next time",
    )
    group.addoption(
        "--sw-skip",
        "--stepwise-skip",
        action="store_true",
        default=False,
        dest="stepwise_skip",
        help="Ignore the first failing test but stop on the next failing test. "
        "Implicitly enables --stepwise.",
    )


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    if config.option.stepwise_skip:
        # allow --stepwise-skip to work on it's own merits.
        config.option.stepwise = True
    if config.getoption("stepwise"):
        config.pluginmanager.register(StepwisePlugin(config), "stepwiseplugin")


def pytest_sessionfinish(session: Session) -> None:
    """
    This function is called at the end of the pytest session. It checks if the 'stepwise' option is not set. If not, it retrieves the cache from the session configuration. If the current process is not a xdist worker, it clears the list of failing tests stored in the cache under the key `STEPWISE_CACHE_DIR`.
    
    Parameters:
    - session (Session): The pytest session object.
    
    Returns:
    - None: This function does not return any value. It performs in-place modifications on the
    """

    if not session.config.getoption("stepwise"):
        assert session.config.cache is not None
        if hasattr(session.config, "workerinput"):
            # Do not update cache if this process is a xdist worker to prevent
            # race conditions (#10641).
            return
        # Clear the list of failing tests if the plugin is not active.
        session.config.cache.set(STEPWISE_CACHE_DIR, [])


class StepwisePlugin:
    def __init__(self, config: Config) -> None:
        """
        Initialize the Stepwise object.
        
        Args:
        config (Config): Configuration object containing necessary settings and options.
        
        Attributes:
        config (Config): Configuration object.
        session (Optional[Session]): Session object, initially set to None.
        report_status (str): Status of the report, initially an empty string.
        cache (Cache): Cache object derived from the configuration.
        lastfailed (Optional[str]): Last failed step, retrieved from the cache.
        skip (bool): Flag indicating whether to skip
        """

        self.config = config
        self.session: Optional[Session] = None
        self.report_status = ""
        assert config.cache is not None
        self.cache: Cache = config.cache
        self.lastfailed: Optional[str] = self.cache.get(STEPWISE_CACHE_DIR, None)
        self.skip: bool = config.getoption("stepwise_skip")

    def pytest_sessionstart(self, session: Session) -> None:
        self.session = session

    def pytest_collection_modifyitems(
        self, config: Config, items: List[nodes.Item]
    ) -> None:
        if not self.lastfailed:
            self.report_status = "no previously failed tests, not skipping."
            return

        # check all item nodes until we find a match on last failed
        failed_index = None
        for index, item in enumerate(items):
            if item.nodeid == self.lastfailed:
                failed_index = index
                break

        # If the previously failed test was not found among the test items,
        # do not skip any tests.
        if failed_index is None:
            self.report_status = "previously failed test not found, not skipping."
        else:
            self.report_status = f"skipping {failed_index} already passed items."
            deselected = items[:failed_index]
            del items[:failed_index]
            config.hook.pytest_deselected(items=deselected)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        if report.failed:
            if self.skip:
                # Remove test from the failed ones (if it exists) and unset the skip option
                # to make sure the following tests will not be skipped.
                if report.nodeid == self.lastfailed:
                    self.lastfailed = None

                self.skip = False
            else:
                # Mark test as the last failing and interrupt the test session.
                self.lastfailed = report.nodeid
                assert self.session is not None
                self.session.shouldstop = (
                    "Test failed, continuing from this test next run."
                )

        else:
            # If the test was actually run and did pass.
            if report.when == "call":
                # Remove test from the failed ones, if exists.
                if report.nodeid == self.lastfailed:
                    self.lastfailed = None

    def pytest_report_collectionfinish(self) -> Optional[str]:
        if self.config.getoption("verbose") >= 0 and self.report_status:
            return f"stepwise: {self.report_status}"
        return None

    def pytest_sessionfinish(self) -> None:
        """
        Function to finalize the pytest session.
        
        This method is called at the end of the pytest session. It checks if the current process is a xdist worker. If not, it updates the cache with the last failed steps.
        
        Parameters:
        self (pytest.Session): The pytest session object.
        
        Returns:
        None: This method does not return any value.
        """

        if hasattr(self.config, "workerinput"):
            # Do not update cache if this process is a xdist worker to prevent
            # race conditions (#10641).
            return
        self.cache.set(STEPWISE_CACHE_DIR, self.lastfailed)
