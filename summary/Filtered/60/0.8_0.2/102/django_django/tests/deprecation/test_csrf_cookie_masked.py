import sys
from types import ModuleType

from django.conf import CSRF_COOKIE_MASKED_DEPRECATED_MSG, Settings, settings
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango50Warning


class CsrfCookieMaskedDeprecationTests(SimpleTestCase):
    msg = CSRF_COOKIE_MASKED_DEPRECATED_MSG

    def test_override_settings_warning(self):
        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(CSRF_COOKIE_MASKED=True):
                pass

    def test_settings_init_warning(self):
        """
        Test the initialization of the Settings object with a custom settings module.
        
        This function simulates the initialization of a Django settings object using a custom settings module. It sets specific attributes in the module and then attempts to initialize the Settings object. If the initialization does not raise the expected warning, the test will fail.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the USE_TZ setting is False and CSRF_COOKIE_MASKED is True, this warning
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
