import sys
from types import ModuleType

from django.conf import CSRF_COOKIE_MASKED_DEPRECATED_MSG, Settings, settings
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango50Warning


class CsrfCookieMaskedDeprecationTests(SimpleTestCase):
    msg = CSRF_COOKIE_MASKED_DEPRECATED_MSG

    def test_override_settings_warning(self):
        """
        Test the override of settings with a warning.
        
        This function checks if attempting to override the `CSRF_COOKIE_MASKED` setting
        raises a `RemovedInDjango50Warning` with the specified message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the `CSRF_COOKIE_MASKED` setting is overridden,
        this warning is raised with the message provided in `self.msg`.
        
        Example:
        >>> with self.settings(CSRF
        """

        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(CSRF_COOKIE_MASKED=True):
                pass

    def test_settings_init_warning(self):
        """
        Tests the initialization of settings with a custom module.
        
        This function creates a fake settings module with specific attributes and sets it in the sys.modules. It then attempts to initialize the Settings object with this module. If the initialization fails as expected with a RemovedInDjango50Warning, the test passes. The function ensures that the warning message matches the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the initialization of the Settings object
        """

        settings_module = ModuleType("fake_settings_module")
        settings_module.USE_TZ = False
        settings_module.CSRF_COOKIE_MASKED = True
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    def test_access(self):
        # Warning is not raised on access.
        self.assertEqual(settings.CSRF_COOKIE_MASKED, False)
