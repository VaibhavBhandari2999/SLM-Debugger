import sys
from types import ModuleType

from django.conf import USE_L10N_DEPRECATED_MSG, Settings, settings
from django.test import TestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango50Warning


class DeprecationTests(TestCase):
    msg = USE_L10N_DEPRECATED_MSG

    def test_override_settings_warning(self):
        """
        Test the override_settings decorator for warning when USE_L10N is set.
        
        This function checks if a RemovedInDjango50Warning is raised when USE_L10N is set in UserSettingsHolder, which is used by the @override_settings decorator.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If USE_L10N is set, this warning is expected to be raised.
        
        Usage:
        This test function is used to
        """

        # Warning is raised when USE_L10N is set in UserSettingsHolder (used by
        # the @override_settings decorator).
        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(USE_L10N=True):
                pass

    def test_settings_init_warning(self):
        """
        Tests the initialization of settings with a custom module.
        
        This function creates a fake settings module and sets specific attributes to test the initialization of Django settings. It raises a RemovedInDjango50Warning if the settings are initialized with the fake module. The function ensures that the warning message matches a predefined message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If the settings are initialized with the fake module, this warning is raised.
        
        Usage:
        """

        settings_module = ModuleType("fake_settings_module")
        settings_module.SECRET_KEY = "foo"
        settings_module.USE_TZ = True
        settings_module.USE_L10N = False
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    def test_access_warning(self):
        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            settings.USE_L10N
        # Works a second time.
        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            settings.USE_L10N

    @ignore_warnings(category=RemovedInDjango50Warning)
    def test_access(self):
        with self.settings(USE_L10N=False):
            self.assertIs(settings.USE_L10N, False)
            # Works a second time.
            self.assertIs(settings.USE_L10N, False)
