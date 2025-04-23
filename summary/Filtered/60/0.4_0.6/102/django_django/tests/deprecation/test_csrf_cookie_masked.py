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
        
        This function raises a RemovedInDjango50Warning with a custom message when the CSRF_COOKIE_MASKED setting is overridden. The warning is expected to be triggered when the setting is set to True within a context where the settings are being modified.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If CSRF_COOKIE_MASKED is set to True within the context, this warning is raised with a
        """

        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(CSRF_COOKIE_MASKED=True):
                pass

    def test_settings_init_warning(self):
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
