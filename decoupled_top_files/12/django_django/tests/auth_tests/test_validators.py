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
        """
        Tests the `get_default_password_validators` function.
        
        This function returns a list of password validators with a length of 2. The first validator is an instance of `CommonPasswordValidator`, and the second one is an instance of `MinimumLengthValidator` with a minimum length of 12 characters.
        """

        validators = get_default_password_validators()
        self.assertEqual(len(validators), 2)
        self.assertEqual(validators[0].__class__.__name__, 'CommonPasswordValidator')
        self.assertEqual(validators[1].__class__.__name__, 'MinimumLengthValidator')
        self.assertEqual(validators[1].min_length, 12)

    def test_get_password_validators_custom(self):
        """
        Tests the `get_password_validators` function with custom configuration.
        
        This test checks that the `get_password_validators` function correctly returns a list of password validators based on the provided configuration. It verifies that the length of the returned validators list is 1 when a single validator is specified, and that the first validator's class name matches the expected 'CommonPasswordValidator'. Additionally, it confirms that an empty list is returned when no validators are specified.
        
        Args:
        None
        
        Returns:
        """

        validator_config = [{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}]
        validators = get_password_validators(validator_config)
        self.assertEqual(len(validators), 1)
        self.assertEqual(validators[0].__class__.__name__, 'CommonPasswordValidator')

        self.assertEqual(get_password_validators([]), [])

    def test_validate_password(self):
        """
        Validate a password according to Django's password validation rules.
        
        Args:
        password (str): The password to be validated.
        
        Returns:
        None: If the password is valid.
        ValidationError: If the password is invalid, with specific error messages and codes.
        
        Raises:
        ValidationError: If the password does not meet the required criteria.
        
        Examples:
        >>> test_validate_password('sufficiently-long')
        None
        
        >>> with self.assertRaises(ValidationError) as cm:
        ...
        """

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
        """
        Tests if the password has been changed using a custom validator.
        
        This function uses a custom `Validator` class to check if the password has been changed. The `Validator` class is responsible for validating the password and storing the updated password and user information. The function takes a `password` and a `user` object as inputs and applies the custom validator to the password change process. After the validation, the function asserts that the `user` and `password` attributes of the `Validator` instance
        """

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
        """
        Tests the `password_validators_help_texts` function.
        
        This function checks if the `password_validators_help_texts` returns a list of help texts for password validators, with a length of 2 and the second element containing '12 characters'. It also verifies that an empty list is returned when no validators are provided.
        """

        help_texts = password_validators_help_texts()
        self.assertEqual(len(help_texts), 2)
        self.assertIn('12 characters', help_texts[1])

        self.assertEqual(password_validators_help_texts(password_validators=[]), [])

    def test_password_validators_help_text_html(self):
        """
        Tests the password validators help text HTML function, ensuring that it returns a string containing exactly two <li> tags and includes the phrase '12 characters'.
        """

        help_text = password_validators_help_text_html()
        self.assertEqual(help_text.count('<li>'), 2)
        self.assertIn('12 characters', help_text)

    def test_password_validators_help_text_html_escaping(self):
        """
        Tests that the help text returned by password validators is properly HTML-escaped.
        
        This function creates an instance of `AmpersandValidator`, which returns
        a help text containing an ampersand ('&'). The `password_validators_help_text_html`
        function is then called with this validator to generate the help text. The generated
        help text is expected to be HTML-escaped, meaning that the ampersand should be
        converted to its HTML entity equivalent ('&amp
        """

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
        Validate that the password meets the minimum length requirement.
        
        Args:
        password (str): The password to validate.
        
        Raises:
        ValidationError: If the password does not meet the minimum length requirement.
        
        Returns:
        None
        
        Important Functions:
        - MinimumLengthValidator: Validates the password length.
        - validate: Checks if the given password meets the minimum length requirement.
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
        """
        Tests the help text generated by the MinimumLengthValidator.
        
        This function checks if the help text returned by the
        MinimumLengthValidator is as expected, ensuring that it correctly
        indicates the minimum length requirement for a password.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the help text does not match the expected output.
        
        Important Functions:
        - MinimumLengthValidator(): The validator class used to generate the help text.
        - get_help_text
        """

        self.assertEqual(
            MinimumLengthValidator().get_help_text(),
            "Your password must contain at least 8 characters."
        )


class UserAttributeSimilarityValidatorTest(TestCase):
    def test_validate(self):
        """
        This function tests the validation of user attributes against potential similarity with other user attributes such as username, email, and first name. It creates a user object and uses the `UserAttributeSimilarityValidator` to check if the given password is similar to any of these attributes.
        
        :param self: The instance of the class containing this method.
        :type self: object
        :return: None
        
        Important Functions:
        - `User.objects.create_user`: Creates a new user object with specified
        """

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
        """
        Validates that the password is not too similar to the username.
        
        This function tests the `UserAttributeSimilarityValidator` by creating a custom model `TestUser` with a property `username`. It then attempts to validate a password ('foobar') against this user, expecting a `ValidationError` to be raised due to the similarity between the password and the username.
        
        Args:
        None (This function uses internal attributes and does not take any explicit arguments).
        
        Returns:
        None (Raises a
        """

        class TestUser(models.Model):
            pass

            @property
            def username(self):
                return 'foobar'

        with self.assertRaises(ValidationError) as cm:
            UserAttributeSimilarityValidator().validate('foobar', user=TestUser()),
        self.assertEqual(cm.exception.messages, ['The password is too similar to the username.'])

    def test_help_text(self):
        """
        Tests the help text generated by the UserAttributeSimilarityValidator.
        
        This function asserts that the help text returned by the
        UserAttributeSimilarityValidator is as expected, specifically checking
        that it matches the provided string indicating that the password should
        not be too similar to other personal information.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the help text does not match the expected string.
        """

        self.assertEqual(
            UserAttributeSimilarityValidator().get_help_text(),
            "Your password can't be too similar to your other personal information."
        )


class CommonPasswordValidatorTest(SimpleTestCase):
    def test_validate(self):
        """
        Validate a password against a list of common passwords.
        
        Args:
        password (str): The password to validate.
        
        Returns:
        None: If the password is not in the list of common passwords.
        ValidationError: If the password is in the list of common passwords.
        
        Raises:
        ValidationError: If the password is in the list of common passwords.
        
        Important Functions:
        - `CommonPasswordValidator.validate`: Validates the given password against a list of common passwords.
        - `self.assertIs
        """

        expected_error = "This password is too common."
        self.assertIsNone(CommonPasswordValidator().validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            CommonPasswordValidator().validate('godzilla')
        self.assertEqual(cm.exception.messages, [expected_error])

    def test_validate_custom_list(self):
        """
        Validate a password against a custom list of common passwords.
        
        This function tests the `CommonPasswordValidator` class by providing a custom
        list of common passwords and validating two different passwords: one that is
        considered safe and another that is from the custom list.
        
        Args:
        None (The test case uses predefined inputs and outputs).
        
        Returns:
        None (The test case asserts the behavior of the `CommonPasswordValidator`).
        
        Important Functions:
        - `CommonPasswordValidator`:
        """

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'common-passwords-custom.txt')
        validator = CommonPasswordValidator(password_list_path=path)
        expected_error = "This password is too common."
        self.assertIsNone(validator.validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            validator.validate('from-my-custom-list')
        self.assertEqual(cm.exception.messages, [expected_error])
        self.assertEqual(cm.exception.error_list[0].code, 'password_too_common')

    def test_validate_django_supplied_file(self):
        """
        Validate that Django-supplied common passwords are correctly converted to lowercase.
        
        This function tests the `CommonPasswordValidator` to ensure that each of the
        pre-defined common passwords is returned in lowercase. The `passwords` attribute
        of the `CommonPasswordValidator` instance is iterated over, and for each password,
        it is verified that the original password matches its lowercase version.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        validator (CommonPasswordValidator
        """

        validator = CommonPasswordValidator()
        for password in validator.passwords:
            self.assertEqual(password, password.lower())

    def test_help_text(self):
        """
        Tests the help text generated by the CommonPasswordValidator.
        
        This function checks if the CommonPasswordValidator returns the expected
        help text, which is a string indicating that the password cannot be a
        commonly used password.
        """

        self.assertEqual(
            CommonPasswordValidator().get_help_text(),
            "Your password can't be a commonly used password."
        )


class NumericPasswordValidatorTest(SimpleTestCase):
    def test_validate(self):
        """
        Validate a password to ensure it is not entirely numeric.
        
        Args:
        password (str): The password to validate.
        
        Returns:
        None: If the password is not entirely numeric.
        ValidationError: If the password is entirely numeric.
        
        Raises:
        ValidationError: If the password is entirely numeric, with an error message indicating the issue.
        
        Important Functions:
        - `NumericPasswordValidator().validate(password)`: Validates the given password.
        - `self.assertIsNone()`: Checks if the
        """

        expected_error = "This password is entirely numeric."
        self.assertIsNone(NumericPasswordValidator().validate('a-safe-password'))

        with self.assertRaises(ValidationError) as cm:
            NumericPasswordValidator().validate('42424242')
        self.assertEqual(cm.exception.messages, [expected_error])
        self.assertEqual(cm.exception.error_list[0].code, 'password_entirely_numeric')

    def test_help_text(self):
        """
        Tests the help text generated by the NumericPasswordValidator.
        
        This function checks if the NumericPasswordValidator returns the expected
        help text, which is "Your password can't be entirely numeric." The
        NumericPasswordValidator is a function that validates whether a password
        contains only numeric characters.
        """

        self.assertEqual(
            NumericPasswordValidator().get_help_text(),
            "Your password can't be entirely numeric."
        )


class UsernameValidatorsTests(SimpleTestCase):
    def test_unicode_validator(self):
        """
        Tests the UnicodeUsernameValidator function.
        
        This function validates usernames against a set of rules defined by the UnicodeUsernameValidator. It checks both valid and invalid usernames, ensuring that only valid ones pass the validation.
        
        Args:
        None (The test cases are run internally using predefined valid and invalid usernames).
        
        Returns:
        None (The function asserts the results through exceptions).
        
        Important Functions:
        - `validators.UnicodeUsernameValidator()`: The validator function used to check the usernames.
        - `self
        """

        valid_usernames = ['joe', 'René', 'ᴮᴵᴳᴮᴵᴿᴰ', 'أحمد']
        invalid_usernames = [
            "o'connell", "عبد ال",
            "zerowidth\u200Bspace", "nonbreaking\u00A0space",
            "en\u2013dash",
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
        Validate ASCII usernames.
        
        This function tests the `ASCIIUsernameValidator` by validating a list of
        valid usernames and raising a `ValidationError` for a list of invalid
        usernames.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `validators.ASCIIUsernameValidator()`: Creates an instance of the
        ASCII username validator.
        - `v(valid)`: Validates a given valid username.
        - `v(invalid)`: Validates a given invalid username
        """

        valid_usernames = ['glenn', 'GLEnN', 'jean-marc']
        invalid_usernames = ["o'connell", 'Éric', 'jean marc', "أحمد"]
        v = validators.ASCIIUsernameValidator()
        for valid in valid_usernames:
            with self.subTest(valid=valid):
                v(valid)
        for invalid in invalid_usernames:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    v(invalid)
