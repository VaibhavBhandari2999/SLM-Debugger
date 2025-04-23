import pytest


def pytest_addoption(parser):
    """
    Add command line options for stepwise testing.
    
    This function is called by pytest to add custom options to the command line interface. It allows users to specify whether they want to run tests in a stepwise manner, where the test run stops on the first failure and allows the user to manually proceed to the next test. The `--stepwise` option stops on the first failure and continues from the last failing test on subsequent runs. The `--stepwise-skip` option skips the first failing test
    """

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
        self.config = config
        self.active = config.getvalue("stepwise")
        self.session = None
        self.report_status = ""

        if self.active:
            self.lastfailed = config.cache.get("cache/stepwise", None)
            self.skip = config.getvalue("stepwise_skip")

    def pytest_sessionstart(self, session):
        self.session = session

    def pytest_collection_modifyitems(self, session, config, items):
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

    def pytest_runtest_logreport(self, report):
        """
        This function is triggered by pytest to log test reports. It processes the test report to handle test failures and skips based on certain conditions.
        
        Parameters:
        - report (pytest.TestReport): The test report object containing information about the test that was just run.
        
        Key Behavior:
        - Skips processing if the plugin is not active or the test is marked as xfailed.
        - If the test fails and the skip option is not set, marks the test as the last failed and stops the test session.
        -
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
        if self.active and self.config.getoption("verbose") >= 0 and self.report_status:
            return "stepwise: %s" % self.report_status

    def pytest_sessionfinish(self, session):
        """
        Method: pytest_sessionfinish
        Summary: This method is called at the end of the pytest session. It checks if the plugin is active and then either stores the last failed tests in the cache or clears the list of failing tests.
        
        Parameters:
        - session: The pytest session object representing the entire test run.
        
        Keywords:
        - active: A boolean indicating whether the plugin is active or not.
        - config: The pytest configuration object.
        - cache: The pytest cache object used to store and retrieve data across
        """

        if self.active:
            self.config.cache.set("cache/stepwise", self.lastfailed)
        else:
            # Clear the list of failing tests if the plugin is not active.
            self.config.cache.set("cache/stepwise", [])
t("cache/stepwise", [])
