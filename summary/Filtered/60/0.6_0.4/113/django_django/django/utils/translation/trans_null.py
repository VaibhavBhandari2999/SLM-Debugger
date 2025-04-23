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
    
    This function returns `singular` if the `number` is 1, and `plural` otherwise.
    
    Parameters:
    singular (str): The string to return when the `number` is 1.
    plural (str): The string to return for any other `number`.
    number (int): The number to determine which string to return.
    
    Returns:
    str: Either `singular` or `plural` based on the value of `number`.
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
    return None


def get_language_from_path(request):
    return None


def get_supported_language_variant(lang_code, strict=False):
    """
    Get the supported language variant based on the provided language code.
    
    Parameters:
    lang_code (str): The language code to check against the supported language.
    strict (bool, optional): If True, the function will raise a LookupError if the language code does not match the settings.LANGUAGE_CODE. Defaults to False.
    
    Returns:
    str: The supported language variant if it matches the settings.LANGUAGE_CODE, otherwise returns None.
    
    Raises:
    LookupError: If strict is True and the language code
    """

    if lang_code and lang_code.lower() == settings.LANGUAGE_CODE.lower():
        return lang_code
    else:
        raise LookupError(lang_code)
