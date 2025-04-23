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
        Create and configure browser options.
        
        This function initializes browser options using the `import_options` method and configures them based on the `headless` attribute.
        
        Parameters:
        self (object): The current instance of the class.
        
        Returns:
        selenium.webdriver.chrome.options.Options or selenium.webdriver.firefox.options.Options: Configured browser options.
        
        Attributes:
        headless (bool): If True, sets the browser to run in headless mode.
        
        Raises:
        AttributeError: If the browser does not support headless
        """

        options = self.import_options(self.browser)()
        if self.headless:
            try:
                options.headless = True
            except AttributeError:
                pass  # Only Chrome and Firefox support the headless mode.
        return options

    def create_webdriver(self):
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
        setUpClass(cls)
        
        This method sets up the class for testing by initializing the WebDriver and setting implicit wait time. It is a class method that should be called before any test cases are run.
        
        Parameters:
        - cls: The test class itself, used to access class attributes and methods.
        
        Key Parameters:
        - cls.selenium: The WebDriver instance used for browser interactions.
        - cls.implicit_wait: The time (in seconds) to wait for elements to appear before throwing a timeout exception.
        
        Returns:
        - None
        """

        cls.selenium = cls.create_webdriver()
        cls.selenium.implicitly_wait(cls.implicit_wait)
        super().setUpClass()

    @classmethod
    def _tearDownClassInternal(cls):
        """
        Tear down class-level resources after tests. This method quits the WebDriver to prevent a deadlock, especially when the browser maintains an open connection. It then calls the superclass's _tearDownClassInternal method to perform additional cleanup.
        
        Parameters:
        cls (class): The class object for which the teardown is being performed.
        
        Key Actions:
        - Quits the WebDriver instance if it exists.
        - Calls the superclass's _tearDownClassInternal method to perform further cleanup.
        
        Note:
        This method is intended to
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
