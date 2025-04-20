from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.test.utils import ignore_warnings
from django.utils.deprecation import RemovedInDjango40Warning


class MockedPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def __init__(self, now):
        self._now_val = now
        super().__init__()

    def _now(self):
        return self._now_val


class TokenGeneratorTest(TestCase):

    def test_make_token(self):
        """
        Function to test the creation and validation of a token for password reset.
        
        This function creates a user and uses the PasswordResetTokenGenerator to generate a token for the user. It then checks if the generated token is valid for the user.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A user is created using the User model with a specific username, email, and password.
        - A PasswordResetTokenGenerator instance is created to generate and check tokens.
        - The `
        """

        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        self.assertIs(p0.check_token(user, tk1), True)

    def test_10265(self):
        """
        The token generated for a user created in the same request
        will work correctly.
        """
        user = User.objects.create_user('comebackkid', 'test3@example.com', 'testpw')
        user_reload = User.objects.get(username='comebackkid')
        p0 = MockedPasswordResetTokenGenerator(datetime.now())
        tk1 = p0.make_token(user)
        tk2 = p0.make_token(user_reload)
        self.assertEqual(tk1, tk2)

    def test_timeout(self):
        """The token is valid after n seconds, but no greater."""
        # Uses a mocked version of PasswordResetTokenGenerator so we can change
        # the value of 'now'.
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        now = datetime.now()
        p0 = MockedPasswordResetTokenGenerator(now)
        tk1 = p0.make_token(user)
        p1 = MockedPasswordResetTokenGenerator(
            now + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        )
        self.assertIs(p1.check_token(user, tk1), True)
        p2 = MockedPasswordResetTokenGenerator(
            now + timedelta(seconds=(settings.PASSWORD_RESET_TIMEOUT + 1))
        )
        self.assertIs(p2.check_token(user, tk1), False)
        with self.settings(PASSWORD_RESET_TIMEOUT=60 * 60):
            p3 = MockedPasswordResetTokenGenerator(
                now + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
            )
            self.assertIs(p3.check_token(user, tk1), True)
            p4 = MockedPasswordResetTokenGenerator(
                now + timedelta(seconds=(settings.PASSWORD_RESET_TIMEOUT + 1))
            )
            self.assertIs(p4.check_token(user, tk1), False)

    def test_check_token_with_nonexistent_token_and_user(self):
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        self.assertIs(p0.check_token(None, tk1), False)
        self.assertIs(p0.check_token(user, None), False)

    def test_token_with_different_secret(self):
        """
        A valid token can be created with a secret other than SECRET_KEY by
        using the PasswordResetTokenGenerator.secret attribute.
        """
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        new_secret = 'abcdefghijkl'
        # Create and check a token with a different secret.
        p0 = PasswordResetTokenGenerator()
        p0.secret = new_secret
        tk0 = p0.make_token(user)
        self.assertIs(p0.check_token(user, tk0), True)
        # Create and check a token with the default secret.
        p1 = PasswordResetTokenGenerator()
        self.assertEqual(p1.secret, settings.SECRET_KEY)
        self.assertNotEqual(p1.secret, new_secret)
        tk1 = p1.make_token(user)
        # Tokens created with a different secret don't validate.
        self.assertIs(p0.check_token(user, tk1), False)
        self.assertIs(p1.check_token(user, tk0), False)

    @ignore_warnings(category=RemovedInDjango40Warning)
    def test_token_default_hashing_algorithm(self):
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        with self.settings(DEFAULT_HASHING_ALGORITHM='sha1'):
            generator = PasswordResetTokenGenerator()
            self.assertEqual(generator.algorithm, 'sha1')
            token = generator.make_token(user)
            self.assertIs(generator.check_token(user, token), True)

    def test_legacy_token_validation(self):
        """
        Tests the validation of legacy password reset tokens.
        
        This function checks whether tokens generated using the old password reset token generator (with 'sha1' algorithm) can be validated by both the old and new token generators. It creates a user, generates a legacy token, and then verifies that the token can be correctly checked by both token generators.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A user is created with a specified username, email, and password.
        - A legacy token is
        """

        # RemovedInDjango40Warning: pre-Django 3.1 tokens will be invalid.
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p_old_generator = PasswordResetTokenGenerator()
        p_old_generator.algorithm = 'sha1'
        p_new_generator = PasswordResetTokenGenerator()

        legacy_token = p_old_generator.make_token(user)
        self.assertIs(p_old_generator.check_token(user, legacy_token), True)
        self.assertIs(p_new_generator.check_token(user, legacy_token), True)
