import functools
import gzip
import re
from difflib import SequenceMatcher
from pathlib import Path

from django.conf import settings
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, ValidationError,
)
from django.utils.functional import lazy
from django.utils.html import format_html, format_html_join
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _, ngettext


@functools.lru_cache(maxsize=None)
def get_default_password_validators():
    return get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)


def get_password_validators(validator_config):
    """
    Import and instantiate password validators based on the provided configuration.
    
    Args:
    validator_config (list): A list of dictionaries containing the configuration for each password validator.
    
    Returns:
    list: A list of instantiated password validators.
    
    Raises:
    ImproperlyConfigured: If the module specified in 'NAME' cannot be imported.
    
    Summary:
    This function takes a list of validator configurations, imports the specified validator classes, and instantiates them with optional options. It returns a list of instantiated
    """

    validators = []
    for validator in validator_config:
        try:
            klass = import_string(validator['NAME'])
        except ImportError:
            msg = "The module in NAME could not be imported: %s. Check your AUTH_PASSWORD_VALIDATORS setting."
            raise ImproperlyConfigured(msg % validator['NAME'])
        validators.append(klass(**validator.get('OPTIONS', {})))

    return validators


def validate_password(password, user=None, password_validators=None):
    """
    Validate whether the password meets all validator requirements.

    If the password is valid, return ``None``.
    If the password is invalid, raise ValidationError with all error messages.
    """
    errors = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)


def password_changed(password, user=None, password_validators=None):
    """
    Inform all validators that have implemented a password_changed() method
    that the password has been changed.
    """
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        password_changed = getattr(validator, 'password_changed', lambda *a: None)
        password_changed(password, user)


def password_validators_help_texts(password_validators=None):
    """
    Return a list of all help texts of all configured validators.
    """
    help_texts = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        help_texts.append(validator.get_help_text())
    return help_texts


def _password_validators_help_text_html(password_validators=None):
    """
    Return an HTML string with all help texts of all configured validators
    in an <ul>.
    """
    help_texts = password_validators_help_texts(password_validators)
    help_items = format_html_join('', '<li>{}</li>', ((help_text,) for help_text in help_texts))
    return format_html('<ul>{}</ul>', help_items) if help_items else ''


password_validators_help_text_html = lazy(_password_validators_help_text_html, str)


class MinimumLengthValidator:
    """
    Validate whether the password is of a minimum length.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        """
        Validate a given password.
        
        Args:
        password (str): The password to be validated.
        user (User, optional): The user associated with the password. Defaults to None.
        
        Raises:
        ValidationError: If the password is shorter than the minimum length specified by `self.min_length`.
        
        Summary:
        This function checks if the provided password meets the minimum length requirement set by the `min_length` attribute. If the password is shorter than the required length, a `ValidationError` is raised
        """

        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "This password is too short. It must contain at least %(min_length)d character.",
                    "This password is too short. It must contain at least %(min_length)d characters.",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        """
        Generates a help text for password requirements.
        
        This function returns a formatted string that specifies the minimum length
        requirement for a password. The string is generated based on the value of
        `self.min_length` and uses the `ngettext` function to handle both singular
        and plural cases.
        
        Args:
        None (the function uses `self.min_length` from the class instance).
        
        Returns:
        str: A formatted string indicating the minimum number of characters
        required for
        """

        return ngettext(
            "Your password must contain at least %(min_length)d character.",
            "Your password must contain at least %(min_length)d characters.",
            self.min_length
        ) % {'min_length': self.min_length}


class UserAttributeSimilarityValidator:
    """
    Validate whether the password is sufficiently different from the user's
    attributes.

    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """
    DEFAULT_USER_ATTRIBUTES = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        """
        Validate a given password against potential similar attributes of a user.
        
        Args:
        password (str): The password to be validated.
        user (User, optional): The user object whose attributes are to be checked. Defaults to None.
        
        Raises:
        ValidationError: If the password is found to be too similar to any of the user's attributes.
        
        This function checks if the provided password is similar to any of the specified user attributes. It uses regular expressions to split the attribute values into parts and
        """

        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("The password is too similar to the %(verbose_name)s."),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

    def get_help_text(self):
        return _('Your password can’t be too similar to your other personal information.')


class CommonPasswordValidator:
    """
    Validate whether the password is a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. The list Django ships with contains 20000 common
    passwords (lowercased and deduplicated), created by Royce Williams:
    https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    The password list must be lowercased to match the comparison in validate().
    """
    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'

    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        """
        Initialize the PasswordList object.
        
        Args:
        password_list_path (str): Path to the file containing the list of passwords.
        
        Returns:
        None
        
        Raises:
        OSError: If the specified file cannot be opened or read.
        
        Summary:
        This function initializes an instance of the PasswordList class by reading a list of passwords from a file. It supports both compressed (.gz) and uncompressed files. The passwords are stored as a set of stripped strings. If the file is compressed,
        """

        try:
            with gzip.open(password_list_path, 'rt', encoding='utf-8') as f:
                self.passwords = {x.strip() for x in f}
        except OSError:
            with open(password_list_path) as f:
                self.passwords = {x.strip() for x in f}

    def validate(self, password, user=None):
        """
        Validate a given password.
        
        Args:
        password (str): The password to be validated.
        user (User, optional): The user object associated with the password. Defaults to None.
        
        Raises:
        ValidationError: If the password is considered too common based on predefined common passwords.
        
        This function checks if the provided password is in a list of common passwords. If it is, a ValidationError is raised with a specific error message indicating that the password is too common.
        """

        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("This password is too common."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _('Your password can’t be a commonly used password.')


class NumericPasswordValidator:
    """
    Validate whether the password is alphanumeric.
    """
    def validate(self, password, user=None):
        """
        Validate a given password.
        
        Args:
        password (str): The password to be validated.
        user (User, optional): The user object associated with the password. Defaults to None.
        
        Raises:
        ValidationError: If the password is entirely numeric.
        """

        if password.isdigit():
            raise ValidationError(
                _("This password is entirely numeric."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _('Your password can’t be entirely numeric.')
