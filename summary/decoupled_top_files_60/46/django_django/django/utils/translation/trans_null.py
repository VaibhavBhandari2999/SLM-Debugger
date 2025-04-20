# These are versions of the functions in django.utils.translation.trans_real
# that don't actually do anything. This is purely for performance, so that
# settings.USE_I18N = False can use this module rather than trans_real.py.

from django.conf import settings


def gettext(message):
    return message


gettext_noop = gettext_lazy = _ = gettext


def ngettext(singular, plural, number):
    """
    Return a string based on the given number.
    
    Args:
    singular (str): The string to return if the number is 1.
    plural (str): The string to return for any other number.
    number (int): The number to determine which string to return.
    
    Returns:
    str: The appropriate string based on the number provided.
    
    Examples:
    >>> ngettext('apple', 'apples', 1)
    'apple'
    >>> ngettext('apple', 'apples',
    """

    if number == 1:
        return singular
    return plural


ngettext_lazy = ngettext


def pgettext(context, message):
    return gettext(message)


def npgettext(context, singular, plural, number):
    return ngettext(singular, plural, number)


def activate(x):
    return None


def deactivate():
    return None


deactivate_all = deactivate


def get_language():
    return settings.LANGUAGE_CODE


def get_language_bidi():
    return settings.LANGUAGE_CODE in settings.LANGUAGES_BIDI


def check_for_language(x):
    return True


def get_language_from_request(request, check_path=False):
    return settings.LANGUAGE_CODE


def get_language_from_path(request):
    return None


def get_supported_language_variant(lang_code, strict=False):
    """
    get_supported_language_variant(lang_code, strict=False)
    Get the supported language variant for a given language code.
    
    Parameters:
    lang_code (str): The language code for which to get the supported variant.
    strict (bool, optional): If True, raise an error if the language code is not supported. Defaults to False.
    
    Returns:
    str: The supported language variant.
    
    Raises:
    LookupError: If strict is True and the language code is not supported.
    
    This function checks if the provided language
    """

    if lang_code == settings.LANGUAGE_CODE:
        return lang_code
    else:
        raise LookupError(lang_code)
