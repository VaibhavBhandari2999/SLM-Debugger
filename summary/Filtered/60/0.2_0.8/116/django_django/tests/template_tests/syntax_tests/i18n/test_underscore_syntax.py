from django.template import Context, Template
from django.test import SimpleTestCase
from django.utils import translation

from ...utils import setup
from .base import MultipleLocaleActivationTestCase


class MultipleLocaleActivationTests(MultipleLocaleActivationTestCase):
    def test_single_locale_activation(self):
        """
        Simple baseline behavior with one locale for all the supported i18n
        constructs.
        """
        with translation.override("fr"):
            self.assertEqual(Template("{{ _('Yes') }}").render(Context({})), "Oui")

    # Literal marked up with _() in a filter expression

    def test_multiple_locale_filter(self):
        """
        Tests the functionality of the 'yesno' filter in Django templates with multiple locale overrides.
        
        This function checks the 'yesno' filter in a Django template with the following steps:
        1. Sets the current locale to 'de' (German).
        2. Loads the 'i18n' template tag library.
        3. Renders a template with the 'yesno' filter using the German translation for 'yes', 'no', and 'maybe'.
        4. Temporarily overrides the current locale to '
        """

        with translation.override("de"):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override(self._old_language), translation.override("nl"):
            self.assertEqual(t.render(Context({})), "nee")

    def test_multiple_locale_filter_deactivate(self):
        with translation.override("de", deactivate=True):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "nee")

    def test_multiple_locale_filter_direct_switch(self):
        """
        Tests the behavior of the 'yesno' filter in Django templates when the locale is switched directly.
        
        This function checks how the 'yesno' filter behaves in a Django template when the locale is switched from German to Dutch. The template uses the 'yesno' filter with a tuple of three strings: 'yes', 'no', and 'maybe'. When the locale is set to German, the filter should return 'ja' for a truthy value, but when the locale is switched to Dutch
        """

        with translation.override("de"):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "nee")

    # Literal marked up with _()

    def test_multiple_locale(self):
        with translation.override("de"):
            t = Template("{{ _('No') }}")
        with translation.override(self._old_language), translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    def test_multiple_locale_deactivate(self):
        with translation.override("de", deactivate=True):
            t = Template("{{ _('No') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    def test_multiple_locale_direct_switch(self):
        with translation.override("de"):
            t = Template("{{ _('No') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    # Literal marked up with _(), loading the i18n template tag library

    def test_multiple_locale_loadi18n(self):
        with translation.override("de"):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override(self._old_language), translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    def test_multiple_locale_loadi18n_deactivate(self):
        """
        Tests the behavior of loading the i18n tag in a Django template with multiple locale settings. The function first sets the locale to 'de' and deactivates it, then loads the i18n tag and renders a template with the string 'No'. The locale is then overridden to 'nl' and the rendered output is checked to ensure it is 'Nee', the Dutch translation of 'No'.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Temp
        """

        with translation.override("de", deactivate=True):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    def test_multiple_locale_loadi18n_direct_switch(self):
        with translation.override("de"):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")


class I18nStringLiteralTests(SimpleTestCase):
    """translation of constant strings"""

    libraries = {"i18n": "django.templatetags.i18n"}

    @setup({"i18n13": '{{ _("Password") }}'})
    def test_i18n13(self):
        with translation.override("de"):
            output = self.engine.render_to_string("i18n13")
        self.assertEqual(output, "Passwort")

    @setup(
        {
            "i18n14": (
                '{% cycle "foo" _("Password") _(\'Password\') as c %} {% cycle c %} '
                "{% cycle c %}"
            )
        }
    )
    def test_i18n14(self):
        with translation.override("de"):
            output = self.engine.render_to_string("i18n14")
        self.assertEqual(output, "foo Passwort Passwort")

    @setup({"i18n15": '{{ absent|default:_("Password") }}'})
    def test_i18n15(self):
        with translation.override("de"):
            output = self.engine.render_to_string("i18n15", {"absent": ""})
        self.assertEqual(output, "Passwort")

    @setup({"i18n16": '{{ _("<") }}'})
    def test_i18n16(self):
        with translation.override("de"):
            output = self.engine.render_to_string("i18n16")
        self.assertEqual(output, "<")
slation.override("de"):
            output = self.engine.render_to_string("i18n16")
        self.assertEqual(output, "<")
