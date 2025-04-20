import warnings

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import User
from django.test import TestCase, modify_settings, override_settings


class CustomRemoteUserBackend(RemoteUserBackend):
    """Override configure_user() without a request argument."""
    def configure_user(self, user):
        user.email = 'user@example.com'
        user.save()
        return user


@override_settings(ROOT_URLCONF='auth_tests.urls')
class RemoteUserCustomTest(TestCase):
    middleware = 'django.contrib.auth.middleware.RemoteUserMiddleware'
    backend = 'auth_tests.test_remote_user_deprecation.CustomRemoteUserBackend'
    header = 'REMOTE_USER'

    def setUp(self):
        """
        Sets up the test environment by modifying the settings.
        
        This method is used to configure the test environment by appending specific settings. It modifies the AUTHENTICATION_BACKENDS and MIDDLEWARE settings.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Modifications:
        - AUTHENTICATION_BACKENDS: Appends the specified backend to the existing list.
        - MIDDLEWARE: Appends the specified middleware to the existing list.
        
        Note:
        The settings modifications are temporary and are automatically enabled and disabled within the test
        """

        self.patched_settings = modify_settings(
            AUTHENTICATION_BACKENDS={'append': self.backend},
            MIDDLEWARE={'append': self.middleware},
        )
        self.patched_settings.enable()

    def tearDown(self):
        self.patched_settings.disable()

    def test_configure_user_deprecation_warning(self):
        """
        A deprecation warning is shown for RemoteUserBackend that have a
        configure_user() method without a request parameter.
        """
        num_users = User.objects.count()
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always')
            response = self.client.get('/remote_user/', **{self.header: 'newuser'})
            self.assertEqual(response.context['user'].username, 'newuser')
        self.assertEqual(len(warns), 1)
        self.assertEqual(
            str(warns[0].message),
            'Update CustomRemoteUserBackend.configure_user() to accept '
            '`request` as the first argument.'
        )
        self.assertEqual(User.objects.count(), num_users + 1)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'user@example.com')
