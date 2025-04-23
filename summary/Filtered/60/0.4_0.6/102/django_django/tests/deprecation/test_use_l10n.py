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
        
        This function checks if a RemovedInDjango50Warning is raised when USE_L10N is set in UserSettingsHolder, which is used by the @override_settings decorator. The warning message is expected to match the provided message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango50Warning: If USE_L10N is set, this warning is expected to be
        """

        # Warning is raised when USE_L10N is set in UserSettingsHolder (used by
        # the @override_settings decorator).
        with self.assertRaisesMessage(RemovedInDjango50Warning, self.msg):
            with self.settings(USE_L10N=True):
                pass

    def test_settings_init_warning(self):
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
        """
        Test the access to a Django settings variable.
        
        This function temporarily sets the `USE_L10N` setting to `False` using Django's `settings` module. It then checks if the setting has been correctly updated. The function demonstrates that the setting is correctly updated and remains so even when accessed again.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The `settings.USE_L10N` setting is modified within the context manager, ensuring that the original setting is
        """

        with self.settings(USE_L10N=False):
            self.assertIs(settings.USE_L10N, False)
            # Works a second time.
            self.assertIs(settings.USE_L10N, False)
