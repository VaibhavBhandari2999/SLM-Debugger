import pytest


def pytest_addoption(parser):
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
def pytest_configure(config):
    config.pluginmanager.register(StepwisePlugin(config), "stepwiseplugin")


class StepwisePlugin:
    def __init__(self, config):
        """
        Initialize the Stepwise plugin.
        
        Args:
        config (pytest.Config): The pytest configuration object containing various settings and values.
        
        Attributes:
        active (bool): Indicates whether the stepwise plugin is active based on the configuration.
        session (pytest.Session): The pytest session object.
        lastfailed (Optional[str]): The last failed test item's ID, retrieved from the cache if available.
        skip (int): The number of tests to skip at the beginning of the test run, as specified in the
        """

        self.config = config
        self.active = config.getvalue("stepwise")
        self.session = None

        if self.active:
            self.lastfailed = config.cache.get("cache/stepwise", None)
            self.skip = config.getvalue("stepwise_skip")

    def pytest_sessionstart(self, session):
        self.session = session

    def pytest_collection_modifyitems(self, session, config, items):
        """
        Function to modify the test collection process in pytest.
        
        This function is called by pytest to modify the list of collected test items. It is used to skip tests that have already passed before a previously failed test.
        
        Parameters:
        session (pytest.Session): The pytest session object.
        config (pytest.Config): The pytest configuration object.
        items (list): A list of pytest.Item objects representing the collected tests.
        
        Returns:
        None: This function does not return anything. It modifies the `items` list
        """

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

    def pytest_collectreport(self, report):
        if self.active and report.failed:
            self.session.shouldstop = (
                "Error when collecting test, stopping test execution."
            )

    def pytest_runtest_logreport(self, report):
        """
        This function is triggered by pytest to log reports during test execution. It processes test reports to handle skipping, marking failing tests, and interrupting the test session if necessary.
        
        Parameters:
        - report (pytest.TestReport): The report object containing information about the test that was just run.
        
        Key Behavior:
        - If the plugin is not active or the test is marked as xfailed, the function does nothing.
        - If the test fails and the skip option is not set, the function marks the test as the
        """

        # Skip this hook if plugin is not active or the test is xfailed.
        if not self.active or "xfail" in report.keywords:
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
                self.session.shouldstop = (
                    "Test failed, continuing from this test next run."
                )

        else:
            # If the test was actually run and did pass.
            if report.when == "call":
                # Remove test from the failed ones, if exists.
                if report.nodeid == self.lastfailed:
                    self.lastfailed = None

    def pytest_report_collectionfinish(self):
        if self.active and self.config.getoption("verbose") >= 0:
            return "stepwise: %s" % self.report_status

    def pytest_sessionfinish(self, session):
        if self.active:
            self.config.cache.set("cache/stepwise", self.lastfailed)
        else:
            # Clear the list of failing tests if the plugin is not active.
            self.config.cache.set("cache/stepwise", [])
