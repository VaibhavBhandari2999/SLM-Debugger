from typing import List
from typing import Optional

import pytest
from _pytest import nodes
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.reports import TestReport


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("general")
    group.addoption(
        "--sw",
        "--stepwise",
        action="store_true",
        dest="stepwise",
        help="exit on test failure and continue from last failing test next time",
    )
    group.addoption(
        "--stepwise-skip",
        action="store_true",
        dest="stepwise_skip",
        help="ignore the first failing test but stop on the next failing test",
    )


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    config.pluginmanager.register(StepwisePlugin(config), "stepwiseplugin")


class StepwisePlugin:
    def __init__(self, config: Config) -> None:
        """
        Initialize the Stepwise object.
        
        Args:
        config (Config): Configuration object containing settings and cache.
        
        Attributes:
        config (Config): Configuration object.
        active (bool): Indicates if stepwise mode is active.
        session (Optional[Session]): Session object.
        report_status (str): Status report string.
        lastfailed (Optional[str]): Last failed stepwise cache entry.
        skip (bool): Indicates if steps should be skipped.
        
        This method initializes the Stepwise object with the provided configuration
        """

        self.config = config
        self.active = config.getvalue("stepwise")
        self.session = None  # type: Optional[Session]
        self.report_status = ""

        if self.active:
            assert config.cache is not None
            self.lastfailed = config.cache.get("cache/stepwise", None)
            self.skip = config.getvalue("stepwise_skip")

    def pytest_sessionstart(self, session: Session) -> None:
        self.session = session

    def pytest_collection_modifyitems(
        self, session: Session, config: Config, items: List[nodes.Item]
    ) -> None:
        if not self.active:
            return
        if not self.lastfailed:
            self.report_status = "no previously failed tests, not skipping."
            return

        already_passed = []
        found = False

        # Make a list of all tests that have been run before the last failing one.
        for item in items:
            if item.nodeid == self.lastfailed:
                found = True
                break
            else:
                already_passed.append(item)

        # If the previously failed test was not found among the test items,
        # do not skip any tests.
        if not found:
            self.report_status = "previously failed test not found, not skipping."
            already_passed = []
        else:
            self.report_status = "skipping {} already passed items.".format(
                len(already_passed)
            )

        for item in already_passed:
            items.remove(item)

        config.hook.pytest_deselected(items=already_passed)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """
        Log a test report during the test session.
        
        This function is called by pytest to log the outcome of a test report. It checks if the test has failed and handles the test based on the current state (skipped or not). If the test fails and the `skip` option is set, it unsets the `skip` option and removes the test from the list of last failed tests. If the test fails and the `skip` option is not set, it marks the test as the last
        """

        if not self.active:
            return

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
        if self.active and self.config.getoption("verbose") >= 0 and self.report_status:
            return "stepwise: %s" % self.report_status
        return None

    def pytest_sessionfinish(self, session: Session) -> None:
        assert self.config.cache is not None
        if self.active:
            self.config.cache.set("cache/stepwise", self.lastfailed)
        else:
            # Clear the list of failing tests if the plugin is not active.
            self.config.cache.set("cache/stepwise", [])
