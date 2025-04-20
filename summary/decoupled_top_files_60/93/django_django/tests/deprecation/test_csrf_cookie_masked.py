import sys
from types import ModuleType

from django.conf import CSRF_COOKIE_MASKED_DEPRECATED_MSG, Settings, settings
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango50Warning


class CsrfCookieMaskedDeprecationTests(SimpleTestCase):
    msg = CSRF_COOKIE_MASKED_DEPRECATED_MSG

    def test_override_settings_warning(self):
        """
        Tests the override of settings with a specific warning message.
        
        This function checks if the override of the CSRF_COOKIE_MASKED setting raises a RemovedInDjango50Warning with the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the CSRF_COOKIE_MASKED setting is overridden without the expected warning message.
        
        Usage:
        This function is typically used in Django test cases to ensure that certain settings deprecation warnings are correctly raised.
        """

        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(CSRF_COOKIE_MASKED=True):
                pass

    def test_settings_init_warning(self):
        """
        Tests the initialization of the Settings class with a custom settings module.
        
        This function creates a fake settings module with specific attributes and sets it in the sys.modules. It then attempts to initialize the Settings class with this module and expects a RemovedInDjango50Warning to be raised with a specific message. The test ensures that the warning is correctly issued for the given settings attributes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the settings attributes
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
