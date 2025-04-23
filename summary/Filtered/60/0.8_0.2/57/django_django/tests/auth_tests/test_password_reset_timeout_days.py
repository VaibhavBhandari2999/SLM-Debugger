import sys
from datetime import datetime, timedelta
from types import ModuleType

from django.conf import (
    PASSWORD_RESET_TIMEOUT_DAYS_DEPRECATED_MSG, Settings, settings,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango40Warning


class DeprecationTests(TestCase):
    msg = PASSWORD_RESET_TIMEOUT_DAYS_DEPRECATED_MSG

    @ignore_warnings(category=RemovedInDjango40Warning)
    def test_timeout(self):
        """The token is valid after n days, but no greater."""
        # Uses a mocked version of PasswordResetTokenGenerator so we can change
        # the value of 'now'.
        class Mocked(PasswordResetTokenGenerator):
            def __init__(self, now):
                self._now_val = now
                super().__init__()

            def _now(self):
                return self._now_val

        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        p1 = Mocked(datetime.now() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS))
        self.assertIs(p1.check_token(user, tk1), True)
        p2 = Mocked(datetime.now() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS + 1))
        self.assertIs(p2.check_token(user, tk1), False)
        with self.settings(PASSWORD_RESET_TIMEOUT_DAYS=1):
            self.assertEqual(settings.PASSWORD_RESET_TIMEOUT, 60 * 60 * 24)
            p3 = Mocked(datetime.now() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS))
            self.assertIs(p3.check_token(user, tk1), True)
            p4 = Mocked(datetime.now() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS + 1))
            self.assertIs(p4.check_token(user, tk1), False)

    def test_override_settings_warning(self):
        """
        Tests the override of settings with a specific warning message.
        
        This function checks if attempting to override the `PASSWORD_RESET_TIMEOUT_DAYS` setting with a value of 2 triggers a `RemovedInDjango40Warning` with the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango40Warning: If the override does not trigger the expected warning.
        
        Usage:
        This function is used to ensure that the `PASSWORD_RESET_TIMEOUT_DAYS` setting override is properly
        """

        with self.assertRaisesMessage(RemovedInDjango40Warning, self.msg):
            with self.settings(PASSWORD_RESET_TIMEOUT_DAYS=2):
                pass

    def test_settings_init_warning(self):
        settings_module = ModuleType('fake_settings_module')
        settings_module.SECRET_KEY = 'foo'
        settings_module.PASSWORD_RESET_TIMEOUT_DAYS = 2
        sys.modules['fake_settings_module'] = settings_module
        try:
            with self.assertRaisesMessage(RemovedInDjango40Warning, self.msg):
                Settings('fake_settings_module')
        finally:
            del sys.modules['fake_settings_module']

    def test_access_warning(self):
        with self.assertRaisesMessage(RemovedInDjango40Warning, self.msg):
            settings.PASSWORD_RESET_TIMEOUT_DAYS
        # Works a second time.
        with self.assertRaisesMessage(RemovedInDjango40Warning, self.msg):
            settings.PASSWORD_RESET_TIMEOUT_DAYS

    @ignore_warnings(category=RemovedInDjango40Warning)
    def test_access(self):
        """
        Test access to the PASSWORD_RESET_TIMEOUT_DAYS setting.
        
        This test function checks the behavior of the PASSWORD_RESET_TIMEOUT_DAYS setting within a specific context. It uses the `with` statement to temporarily set the PASSWORD_RESET_TIMEOUT_DAYS to 2 and then verifies that the setting is correctly updated. The test confirms that the setting retains its value even when accessed again within the same context.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `settings.PASSWORD_RESET_TIMEOUT_DAYS` is set to
        """

        with self.settings(PASSWORD_RESET_TIMEOUT_DAYS=2):
            self.assertEqual(settings.PASSWORD_RESET_TIMEOUT_DAYS, 2)
            # Works a second time.
            self.assertEqual(settings.PASSWORD_RESET_TIMEOUT_DAYS, 2)

    def test_use_both_settings_init_error(self):
        """
        Test the initialization error when both PASSWORD_RESET_TIMEOUT_DAYS and PASSWORD_RESET_TIMEOUT settings are provided.
        
        This function checks that an ImproperlyConfigured exception is raised when both PASSWORD_RESET_TIMEOUT_DAYS and PASSWORD_RESET_TIMEOUT settings are defined in the settings module. The function uses a custom settings module and a temporary sys.modules entry to simulate the settings environment.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ImproperlyConfigured: If both PASSWORD_RESET_TIMEOUT_DAYS and PASSWORD_RESET_TIMEOUT settings are provided
        """

        msg = (
            'PASSWORD_RESET_TIMEOUT_DAYS/PASSWORD_RESET_TIMEOUT are '
            'mutually exclusive.'
        )
        settings_module = ModuleType('fake_settings_module')
        settings_module.SECRET_KEY = 'foo'
        settings_module.PASSWORD_RESET_TIMEOUT_DAYS = 2
        settings_module.PASSWORD_RESET_TIMEOUT = 2000
        sys.modules['fake_settings_module'] = settings_module
        try:
            with self.assertRaisesMessage(ImproperlyConfigured, msg):
                Settings('fake_settings_module')
        finally:
            del sys.modules['fake_settings_module']
