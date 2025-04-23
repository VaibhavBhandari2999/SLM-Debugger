import os

from django.contrib.auth import validators
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator,
    UserAttributeSimilarityValidator, get_default_password_validators,
    get_password_validators, password_changed,
    password_validators_help_text_html, password_validators_help_texts,
    validate_password,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import isolate_apps
from django.utils.html import conditional_escape


@override_settings(AUTH_PASSWORD_VALIDATORS=[
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {
        'min_length': 12,
    }},
])
class PasswordValidationTest(SimpleTestCase):
    def test_get_default_password_validators(self):
        validators = get_default_password_validators()
        self.assertEqual(len(validators), 2)
        self.assertEqual(validators[0].__class__.__name__, 'CommonPasswordValidator')
        self.assertEqual(validators[1].__class__.__name__, 'MinimumLengthValidator')
        self.assertEqual(validators[1].min_length, 12)

    def test_get_password_validators_custom(self):
        """
        Tests the `get_password_validators` function.
        
        This function takes a configuration of password validators and returns a list of instantiated validator objects. It can be used to validate custom configurations of password validators.
        
        Parameters:
        validator_config (list): A list of dictionaries, where each dictionary contains a 'NAME' key specifying the name of the password validator class to be instantiated.
        
        Returns:
        list: A list of instantiated password validator objects.
        
        Example:
        >>> validator_config = [{'NAME': 'django.contrib.auth
        """

        validator_config = [{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}]
        validators = get_password_validators(validator_config)
        self.assertEqual(len(validators), 1)
        self.assertEqual(validators[0].__class__.__name__, 'CommonPasswordValidator')

        self.assertEqual(get_password_validators([]), [])

    def test_validate_password(self):
        self.assertIsNone(validate_password('sufficiently-long'))
        msg_too_short = 'This password is too short. It must contain at least 12 characters.'

        with self.assertRaises(ValidationError) as cm:
            validate_password('django4242')
        self.assertEqual(cm.exception.messages, [msg_too_short])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_short')

        with self.assertRaises(ValidationError) as cm:
            validate_password('password')
        self.assertEqual(cm.exception.messages, ['This password is too common.', msg_too_short])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_common')

        self.assertIsNone(validate_password('password', password_validators=[]))

    def test_password_changed(self):
        self.assertIsNone(password_changed('password'))

    def test_password_changed_with_custom_validator(self):
        class Validator:
            def password_changed(self, password, user):
                self.password = password
                self.user = user

        user = object()
        validator = Validator()
        password_changed('password', user=user, password_validators=(validator,))
        self.assertIs(validator.user, user)
        self.assertEqual(validator.password, 'password')

    def test_password_validators_help_texts(self):
        help_texts = password_validators_help_texts()
        self.assertEqual(len(help_texts), 2)
        self.assertIn('12 characters', help_texts[1])

        self.assertEqual(password_validators_help_texts(password_validators=[]), [])

    def test_password_validators_help_text_html(self):
        help_text = password_validators_help_text_html()
        self.assertEqual(help_text.count('<li>'), 2)
        self.assertIn('12 characters', help_text)

    def test_password_validators_help_text_html_escaping(self):
        class AmpersandValidator:
            def get_help_text(self):
                return 'Must contain &'
        help_text = password_validators_help_text_html([AmpersandValidator()])
        self.assertEqual(help_text, '<ul><li>Must contain &amp;</li></ul>')
        # help_text is marked safe and therefore unchanged by conditional_escape().
        self.assertEqual(help_text, conditional_escape(help_text))

    @override_settings(AUTH_PASSWORD_VALIDATORS=[])
    def test_empty_password_validator_help_text_html(self):
        self.assertEqual(password_validators_help_text_html(), '')


class MinimumLengthValidatorTest(SimpleTestCase):
    def test_validate(self):
        """
        Tests the MinimumLengthValidator function.
        
        This function tests the MinimumLengthValidator class to ensure it correctly validates the length of a password. The function checks for the following scenarios:
        - A password that meets the minimum length requirement should not raise a ValidationError.
        - A password that is too short should raise a ValidationError with an appropriate error message.
        
        Parameters:
        - None (The function uses predefined test cases within the body).
        
        Returns:
        - None (The function asserts expected outcomes and raises exceptions for incorrect behavior).
        
        Key Parameters
        """

        expected_error = "This password is too short. It must contain at least %d characters."
        self.assertIsNone(MinimumLengthValidator().validate('12345678'))
        self.assertIsNone(MinimumLengthValidator(min_length=3).validate('123'))

        with self.assertRaises(ValidationError) as cm:
            MinimumLengthValidator().validate('1234567')
        self.assertEqual(cm.exception.messages, [expected_error % 8])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_short')

        with self.assertRaises(ValidationError) as cm:
            MinimumLengthValidator(min_length=3).validate('12')
        self.assertEqual(cm.exception.messages, [expected_error % 3])

    def test_help_text(self):
        self.assertEqual(
            MinimumLengthValidator().get_help_text(),
            "Your password must contain at least 8 characters."
        )


class UserAttributeSimilarityValidatorTest(TestCase):
    def test_validate(self):
        user = User.objects.create_user(
            username='testclient', password='password', email='testclient@example.com',
            first_name='Test', last_name='Client',
        )
        expected_error = "The password is too similar to the %s."

        self.assertIsNone(UserAttributeSimilarityValidator().validate('testclient'))

        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator().validate('testclient', user=user),
        self.assertEqual(cm.exception.messages, [expected_error % "username"])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_similar')

        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator().validate('example.com', user=user),
        self.assertEqual(cm.exception.messages, [expected_error % "email address"])

        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator(
                user_attributes=['first_name'],
                max_similarity=0.3,
            ).validate('testclient', user=user)
        self.assertEqual(cm.exception.messages, [expected_error % "first name"])
        # max_similarity=1 doesn't allow passwords that are identical to the
        # attribute's value.
        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator(
                user_attributes=['first_name'],
                max_similarity=1,
            ).validate(user.first_name, user=user)
        self.assertEqual(cm.exception.messages, [expected_error % "first name"])
        # max_similarity=0 rejects all passwords.
        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator(
                user_attributes=['first_name'],
                max_similarity=0,
            ).validate('XXX', user=user)
        self.assertEqual(cm.exception.messages, [expected_error % "first name"])
        # Passes validation.
        self.assertIsNone(
            UserAttributeSimilarityValidator(user_attributes=['first_name']).validate('testclient', user=user)
        )

    @isolate_apps('auth_tests')
    def test_validate_property(self):
        class TestUser(models.Model):
            pass

            @property
            def username(self):
                return 'foobar'

        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator().validate('foobar', user=TestUser()),
        self.assertEqual(cm.exception.messages, ['The password is too similar to the username.'])

    def test_help_text(self):
        self.assertEqual(
            UserAttributeSimilarityValidator().get_help_text(),
            'Your password can’t be too similar to your other personal information.'
        )


class CommonPasswordValidatorTest(SimpleTestCase):
    def test_validate(self):
        expected_error = "This password is too common."
        self.assertIsNone(CommonPasswordValidator().validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            CommonPasswordValidator().validate('godzilla')
        self.assertEqual(cm.exception.messages, [expected_error])

    def test_validate_custom_list(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'common-passwords-custom.txt')
        validator = CommonPasswordValidator(password_list_path=path)
        expected_error = "This password is too common."
        self.assertIsNone(validator.validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            validator.validate('from-my-custom-list')
        self.assertEqual(cm.exception.messages, [expected_error])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_common')

    def test_validate_django_supplied_file(self):
        validator = CommonPasswordValidator()
        for password in validator.passwords:
            self.assertEqual(password, password.lower())

    def test_help_text(self):
        self.assertEqual(
            CommonPasswordValidator().get_help_text(),
            'Your password can’t be a commonly used password.'
        )


class NumericPasswordValidatorTest(SimpleTestCase):
    def test_validate(self):
        expected_error = "This password is entirely numeric."
        self.assertIsNone(NumericPasswordValidator().validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            NumericPasswordValidator().validate('42424242')
        self.assertEqual(cm.exception.messages, [expected_error])
        self.assertEqual(cm.exception.error_list[0].code, 'password_entirely_numeric')

    def test_help_text(self):
        """
        Tests the help text generated by the NumericPasswordValidator.
        
        This function checks that the NumericPasswordValidator returns the correct help text, which is 'Your password can’t be entirely numeric.' The function does not take any parameters or return any value.
        
        :Example:
        >>> test_help_text()
        'Your password can’t be entirely numeric.'
        """

        self.assertEqual(
            NumericPasswordValidator().get_help_text(),
            'Your password can’t be entirely numeric.'
        )


class UsernameValidatorsTests(SimpleTestCase):
    def test_unicode_validator(self):
        """
        Tests the UnicodeUsernameValidator function.
        
        This function tests the UnicodeUsernameValidator to ensure it correctly validates usernames containing Unicode characters. It checks a list of valid usernames and a list of invalid usernames.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - valid_usernames (list): A list of valid usernames, including Unicode characters.
        - invalid_usernames (list): A list of invalid usernames, which should raise a ValidationError when passed to the validator.
        
        Key Keywords:
        - None
        """

        valid_usernames = ['joe', 'René', 'ᴮᴵᴳᴮᴵᴿᴰ', 'أحمد']
        invalid_usernames = [
            "o'connell", "عبد ال",
            "zerowidth\u200Bspace", "nonbreaking\u00A0space",
            "en\u2013dash", 'trailingnewline\u000A',
        ]
        v = validators.UnicodeUsernameValidator()
        for valid in valid_usernames:
            with self.subTest(valid=valid):
                v(valid)
        for invalid in invalid_usernames:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    v(invalid)

    def test_ascii_validator(self):
        """
        Tests the ASCIIUsernameValidator function.
        
        This function tests the ASCIIUsernameValidator by validating a list of valid usernames and raising a ValidationError for a list of invalid usernames.
        
        Parameters:
        valid_usernames (list): A list of valid usernames to be tested.
        invalid_usernames (list): A list of invalid usernames to be tested.
        
        Returns:
        None: The function does not return any value, but raises ValidationError for invalid usernames.
        
        Example:
        valid_usernames = ['glenn', 'GLEnN', 'je
        """

        valid_usernames = ['glenn', 'GLEnN', 'jean-marc']
        invalid_usernames = ["o'connell", 'Éric', 'jean marc', "أحمد", 'trailingnewline\n']
        v = validators.ASCIIUsernameValidator()
        for valid in valid_usernames:
            with self.subTest(valid=valid):
                v(valid)
        for invalid in invalid_usernames:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    v(invalid)
