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
        config (pytest.Config): The pytest configuration object containing plugin configuration.
        
        Attributes:
        active (bool): Indicates whether the stepwise plugin is active.
        session (pytest.Session): The pytest session object.
        lastfailed (str or None): The last failed test item identifier, retrieved from the cache.
        skip (int): The number of tests to skip at the beginning of the test run, as specified in the configuration.
        
        This method initializes the Stepwise
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
        Function to modify the collection of tests based on the status of previously failed tests.
        
        Parameters:
        - session: The pytest session object.
        - config: The pytest configuration object.
        - items: A list of collected test items.
        
        Returns:
        - None: The function modifies the `items` list in place.
        
        Behavior:
        - If the `self.active` flag is not set, the function does nothing.
        - If there are no previously failed tests (`self.lastfailed` is not set), the function sets the
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
        """
        Finish the pytest session by storing the last failed tests in the cache.
        
        This method is called at the end of the pytest session. It checks if the stepwise plugin is active. If it is, the last failed tests are stored in the cache under the key 'cache/stepwise'. If the plugin is not active, the list of failing tests is cleared from the cache.
        
        Parameters:
        session (pytest.Session): The pytest session object.
        
        Returns:
        None: This method does not return any
        """

        if self.active:
            self.config.cache.set("cache/stepwise", self.lastfailed)
        else:
            # Clear the list of failing tests if the plugin is not active.
            self.config.cache.set("cache/stepwise", [])
