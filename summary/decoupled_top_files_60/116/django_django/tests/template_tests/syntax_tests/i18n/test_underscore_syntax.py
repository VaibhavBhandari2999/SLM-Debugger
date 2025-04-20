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
        with translation.override("de"):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override(self._old_language), translation.override("nl"):
            self.assertEqual(t.render(Context({})), "nee")

    def test_multiple_locale_filter_deactivate(self):
        """
        Tests the behavior of the `yesno` filter in Django templates when using the `deactivate` option with translation override.
        
        This function overrides the current locale to 'de' with `deactivate=True`, which deactivates the current translation context. Then, it overrides the locale to 'nl' and checks if the `yesno` filter correctly renders 'nee' for the boolean value `0`, indicating that the filter respects the deactivated translation context.
        
        Parameters:
        - None
        
        Returns:
        - None
        """

        with translation.override("de", deactivate=True):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override("nl"):
            self.assertEqual(t.render(Context({})), "nee")

    def test_multiple_locale_filter_direct_switch(self):
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
        """
        Test deactivating a specific locale.
        
        This function tests the deactivation of a specific locale by using the `translation.override` context manager. It sets the locale to 'de' and deactivates it, then sets the locale to 'nl' and checks if the template renders the string "Nee" (which is the Dutch translation of "No").
        
        Parameters:
        None
        
        Returns:
        None
        
        Usage:
        This function is typically used in a test suite to ensure that locale changes and
        """

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
        """
        Tests the functionality of loading and rendering localized strings using Django's template system.
        
        This function checks the correct rendering of a localized string in a Django template. It first sets the locale to 'de' (German) and loads the i18n tag library. Then, it overrides the language to 'nl' (Dutch) and renders the template with the string 'No'. The expected output is 'Nee', which is the Dutch translation of 'No'.
        
        Key Parameters:
        - None
        
        Keywords
        """

        with translation.override("de"):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override(self._old_language), translation.override("nl"):
            self.assertEqual(t.render(Context({})), "Nee")

    def test_multiple_locale_loadi18n_deactivate(self):
        """
        Tests the behavior of loading the i18n tag in a Django template with multiple locale overrides. The function first sets the locale to 'de' and deactivates it, then loads the i18n tag and renders a template with the string 'No'. It then overrides the locale to 'nl' and checks if the rendered template output is 'Nee', which is the Dutch translation of 'No'.
        
        Parameters:
        - None
        
        Keywords:
        - None
        
        Returns:
        - None
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
        """
        Test the i18n13 template rendering function.
        
        This test checks the rendering of the 'i18n13' template with the 'de' language
        override. The function uses Django's translation system to translate the
        content of the template into German and then renders it. The expected output
        is the German translation of the word 'Password'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The rendered output should be equal to "Passwort".
        """

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
        """
        Tests the i18n16 template tag with German language override.
        
        This function overrides the current language context to German ('de') and then renders the 'i18n16' template. The expected output is a single less-than sign ('<').
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses Django's translation.override context manager to set the language to German.
        - It then renders the 'i18n16' template
        """

        with translation.override("de"):
            output = self.engine.render_to_string("i18n16")
        self.assertEqual(output, "<")
