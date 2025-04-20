from datetime import datetime

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class PasswordResetTokenGenerator:
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """
    key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"
    algorithm = None
    secret = None

    def __init__(self):
        """
        Initialize the object with a secret key and hashing algorithm.
        
        This method sets the `secret` attribute to the provided or fallback to the `SECRET_KEY` setting from the Django settings. It also sets the `algorithm` attribute to the provided or fallback to the `DEFAULT_HASHING_ALGORITHM` setting from the Django settings.
        
        Parameters:
        None
        
        Attributes Set:
        - `secret`: The secret key used for hashing.
        - `algorithm`: The hashing algorithm used for hashing.
        
        Note:
        -
        """

        self.secret = self.secret or settings.SECRET_KEY
        # RemovedInDjango40Warning: when the deprecation ends, replace with:
        # self.algorithm = self.algorithm or 'sha256'
        self.algorithm = self.algorithm or settings.DEFAULT_HASHING_ALGORITHM

    def make_token(self, user):
        """
        Return a token that can be used once to do a password reset
        for the given user.
        """
        return self._make_token_with_timestamp(user, self._num_seconds(self._now()))

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            # RemovedInDjango40Warning: when the deprecation ends, replace
            # with:
            #   return False
            if not constant_time_compare(
                self._make_token_with_timestamp(user, ts, legacy=True),
                token,
            ):
                return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.PASSWORD_RESET_TIMEOUT:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp, legacy=False):
        """
        Generates a secure token for a given user with a specific timestamp.
        
        This function creates a token that includes a unique identifier for the user and a timestamp. The token is generated using a secure hashing algorithm and is designed to be short and URL-friendly.
        
        Parameters:
        user (User): The user object for whom the token is being generated.
        timestamp (int): The timestamp in seconds since 2001-1-1. This is used to ensure the token is time-bound and secure
        """

        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
            secret=self.secret,
            # RemovedInDjango40Warning: when the deprecation ends, remove the
            # legacy argument and replace with:
            #   algorithm=self.algorithm,
            algorithm='sha1' if legacy else self.algorithm,
        ).hexdigest()[::2]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that invalidated when it's
        used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT eventually
        invalidates the token.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return str(user.pk) + user.password + str(login_timestamp) + str(timestamp)

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    def _now(self):
        # Used for mocking in tests
        return datetime.now()


default_token_generator = PasswordResetTokenGenerator()
