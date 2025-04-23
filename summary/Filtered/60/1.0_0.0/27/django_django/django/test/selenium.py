import sys
import unittest
from contextlib import contextmanager

from django.test import LiveServerTestCase, tag
from django.utils.functional import classproperty
from django.utils.module_loading import import_string
from django.utils.text import capfirst


class SeleniumTestCaseBase(type(LiveServerTestCase)):
    # List of browsers to dynamically create test classes for.
    browsers = []
    # A selenium hub URL to test against.
    selenium_hub = None
    # The external host Selenium Hub can reach.
    external_host = None
    # Sentinel value to differentiate browser-specific instances.
    browser = None
    # Run browsers in headless mode.
    headless = False

    def __new__(cls, name, bases, attrs):
        """
        Dynamically create new classes and add them to the test module when
        multiple browsers specs are provided (e.g. --selenium=firefox,chrome).
        """
        test_class = super().__new__(cls, name, bases, attrs)
        # If the test class is either browser-specific or a test base, return it.
        if test_class.browser or not any(name.startswith('test') and callable(value) for name, value in attrs.items()):
            return test_class
        elif test_class.browsers:
            # Reuse the created test class to make it browser-specific.
            # We can't rename it to include the browser name or create a
            # subclass like we do with the remaining browsers as it would
            # either duplicate tests or prevent pickling of its instances.
            first_browser = test_class.browsers[0]
            test_class.browser = first_browser
            # Listen on an external interface if using a selenium hub.
            host = test_class.host if not test_class.selenium_hub else '0.0.0.0'
            test_class.host = host
            test_class.external_host = cls.external_host
            # Create subclasses for each of the remaining browsers and expose
            # them through the test's module namespace.
            module = sys.modules[test_class.__module__]
            for browser in test_class.browsers[1:]:
                browser_test_class = cls.__new__(
                    cls,
                    "%s%s" % (capfirst(browser), name),
                    (test_class,),
                    {
                        'browser': browser,
                        'host': host,
                        'external_host': cls.external_host,
                        '__module__': test_class.__module__,
                    }
                )
                setattr(module, browser_test_class.__name__, browser_test_class)
            return test_class
        # If no browsers were specified, skip this class (it'll still be discovered).
        return unittest.skip('No browsers specified.')(test_class)

    @classmethod
    def import_webdriver(cls, browser):
        return import_string("selenium.webdriver.%s.webdriver.WebDriver" % browser)

    @classmethod
    def import_options(cls, browser):
        return import_string('selenium.webdriver.%s.options.Options' % browser)

    @classmethod
    def get_capability(cls, browser):
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        return getattr(DesiredCapabilities, browser.upper())

    def create_options(self):
        """
        Function to create browser options for a web scraping or automation task.
        
        This function initializes browser options using the `import_options` method and sets the headless mode if specified.
        
        Parameters:
        browser (str): The name of the browser to initialize options for. Currently supports 'chrome' and 'firefox'.
        
        Keyword Arguments:
        headless (bool, optional): If True, the browser will run in headless mode. Defaults to False.
        
        Returns:
        selenium.webdriver.chrome.options.Options or selenium.webdriver.firefox
        """

        options = self.import_options(self.browser)()
        if self.headless:
            try:
                options.headless = True
            except AttributeError:
                pass  # Only Chrome and Firefox support the headless mode.
        return options

    def create_webdriver(self):
        """
        Creates a WebDriver instance for browser automation.
        
        This function initializes a WebDriver instance either by connecting to a Selenium hub or by directly importing and initializing the WebDriver for a specified browser.
        
        Parameters:
        self (object): The object instance that contains attributes such as `selenium_hub` and `browser`.
        
        Returns:
        WebDriver: An instance of the WebDriver that can be used for browser automation.
        
        Key Parameters:
        - `selenium_hub` (str): The URL of the Selenium hub if remote execution is required
        """

        if self.selenium_hub:
            from selenium import webdriver
            return webdriver.Remote(
                command_executor=self.selenium_hub,
                desired_capabilities=self.get_capability(self.browser),
            )
        return self.import_webdriver(self.browser)(options=self.create_options())


@tag('selenium')
class SeleniumTestCase(LiveServerTestCase, metaclass=SeleniumTestCaseBase):
    implicit_wait = 10
    external_host = None

    @classproperty
    def live_server_url(cls):
        return 'http://%s:%s' % (cls.external_host or cls.host, cls.server_thread.port)

    @classproperty
    def allowed_host(cls):
        return cls.external_host or cls.host

    @classmethod
    def setUpClass(cls):
        """
        Sets up the class for testing by initializing the WebDriver and setting implicit wait time.
        
        This method is a class method that is called before any tests in the class are run. It initializes the WebDriver using the `create_webdriver` method and sets the implicit wait time for the WebDriver to the value specified in `implicit_wait`. It then calls the superclass's `setUpClass` method.
        
        Parameters:
        cls (object): The class object for which the setup is being performed.
        
        Returns:
        None: This
        """

        cls.selenium = cls.create_webdriver()
        cls.selenium.implicitly_wait(cls.implicit_wait)
        super().setUpClass()

    @classmethod
    def _tearDownClassInternal(cls):
        """
        Tear down class-level resources after tests have run. This method quits the WebDriver instance to release resources and ensures that the LiveServerThread is properly terminated and joined to avoid deadlocks. It is called internally by the superclass.
        
        Parameters:
        cls (class): The class object for which the teardown is being performed.
        
        Returns:
        None: This method does not return any value. It is responsible for cleaning up resources used during test execution.
        
        Key Points:
        - Quits the WebDriver instance if it exists
        """

        # quit() the WebDriver before attempting to terminate and join the
        # single-threaded LiveServerThread to avoid a dead lock if the browser
        # kept a connection alive.
        if hasattr(cls, 'selenium'):
            cls.selenium.quit()
        super()._tearDownClassInternal()

    @contextmanager
    def disable_implicit_wait(self):
        """Disable the default implicit wait."""
        self.selenium.implicitly_wait(0)
        try:
            yield
        finally:
            self.selenium.implicitly_wait(self.implicit_wait)
