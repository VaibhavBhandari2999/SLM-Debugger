from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, override_settings
from django.test.utils import ignore_warnings
from django.utils.deprecation import RemovedInDjango40Warning


class TestAuthenticationMiddleware(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_user', 'test@example.com', 'test_password')

    def setUp(self):
        """
        setUp(self)
        
        Sets up the test environment for authentication middleware testing.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None
        
        Key Parameters:
        - middleware: An instance of AuthenticationMiddleware to be tested.
        - user: The user to be logged in for the test.
        - request: An HttpRequest object to simulate a client request.
        
        Keywords:
        - force_login: Logs the specified user into the session.
        
        Details:
        This method initializes the test environment by setting up an instance of AuthenticationMiddleware
        """

        self.middleware = AuthenticationMiddleware(lambda req: HttpResponse())
        self.client.force_login(self.user)
        self.request = HttpRequest()
        self.request.session = self.client.session

    def test_no_password_change_doesnt_invalidate_session(self):
        """
        Tests that a user session is not invalidated if no password change is required.
        
        This function tests the behavior of a middleware when a user's password does not need to be changed. It sets up a session and user context, runs the middleware, and checks that the user is still authenticated.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a test client session to simulate a user session.
        - It calls a middleware function with the request object.
        - It asserts that the
        """

        self.request.session = self.client.session
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)

    def test_no_password_change_does_not_invalidate_legacy_session(self):
        # RemovedInDjango40Warning: pre-Django 3.1 hashes will be invalid.
        session = self.client.session
        session[HASH_SESSION_KEY] = self.user._legacy_get_session_auth_hash()
        session.save()
        self.request.session = session
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)

    @ignore_warnings(category=RemovedInDjango40Warning)
    def test_session_default_hashing_algorithm(self):
        """
        Tests the default hashing algorithm for session authentication.
        
        This function checks if the session hash changes when the default hashing algorithm is set to 'sha1'. It uses the Django test client to access the session and compares the session hash before and after overriding the default hashing algorithm.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - client: The Django test client used to access the session.
        - HASH_SESSION_KEY: The key used to store the session hash.
        - override_settings: A
        """

        hash_session = self.client.session[HASH_SESSION_KEY]
        with override_settings(DEFAULT_HASHING_ALGORITHM='sha1'):
            self.assertNotEqual(hash_session, self.user.get_session_auth_hash())

    def test_changed_password_invalidates_session(self):
        # After password change, user should be anonymous
        self.user.set_password('new_password')
        self.user.save()
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertTrue(self.request.user.is_anonymous)
        # session should be flushed
        self.assertIsNone(self.request.session.session_key)

    def test_no_session(self):
        msg = (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        with self.assertRaisesMessage(AssertionError, msg):
            self.middleware(HttpRequest())
