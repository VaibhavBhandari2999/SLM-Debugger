# These are versions of the functions in django.utils.translation.trans_real
# that don't actually do anything. This is purely for performance, so that
# settings.USE_I18N = False can use this module rather than trans_real.py.

from django.conf import settings


def gettext(message):
    return message


gettext_noop = gettext_lazy = _ = gettext


def ngettext(singular, plural, number):
    """
    Return a translation of a plural form of a message.
    
    Args:
    singular (str): The singular form of the message.
    plural (str): The plural form of the message.
    number (int): The number that determines which form to use.
    
    Returns:
    str: The appropriate form of the message based on the number provided.
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
    if lang_code and lang_code.lower() == settings.LANGUAGE_CODE.lower():
        return lang_code
    else:
        raise LookupError(lang_code)
d the language code does not match
    """

    if lang_code and lang_code.lower() == settings.LANGUAGE_CODE.lower():
        return lang_code
    else:
        raise LookupError(lang_code)
