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
        
        This function raises a RemovedInDjango50Warning with a specified message when the CSRF_COOKIE_MASKED setting is overridden.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the CSRF_COOKIE_MASKED setting is overridden, a warning is raised with the message specified in self.msg.
        """

        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(CSRF_COOKIE_MASKED=True):
                pass

    def test_settings_init_warning(self):
        """
        Tests the initialization of the Settings class with a custom settings module.
        
        This function creates a mock settings module with specific attributes and sets it in the sys.modules. It then attempts to initialize the Settings class with this module and expects a RemovedInDjango50Warning to be raised with a specific message. The function ensures that the warning message matches the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the warning message does not match
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
