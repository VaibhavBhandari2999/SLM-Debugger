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
        with translation.override('fr'):
            self.assertEqual(Template("{{ _('Yes') }}").render(Context({})), 'Oui')

    # Literal marked up with _() in a filter expression

    def test_multiple_locale_filter(self):
        """
        Test the functionality of the 'yesno' filter with multiple locale settings.
        
        This function checks the 'yesno' filter behavior when different locales are set.
        It first sets the locale to 'de' and then to 'nl' within a nested context, rendering
        a template that uses the 'yesno' filter with the choices 'yes', 'no', and 'maybe'.
        The expected output is 'nee', which is the Dutch translation of 'no'.
        
        Parameters:
        - None
        
        Returns:
        -
        """

        with translation.override('de'):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override(self._old_language), translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    def test_multiple_locale_filter_deactivate(self):
        with translation.override('de', deactivate=True):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    def test_multiple_locale_filter_direct_switch(self):
        with translation.override('de'):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    # Literal marked up with _()

    def test_multiple_locale(self):
        with translation.override('de'):
            t = Template("{{ _('No') }}")
        with translation.override(self._old_language), translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    def test_multiple_locale_deactivate(self):
        """
        Deactivate the 'de' locale and override it with 'nl' for rendering a template. This function tests the behavior of locale deactivation by first setting the locale to 'de' and deactivating it, then overriding it with 'nl' to render a template with the string 'Nee' for 'No'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Temporarily override the current locale with 'de' and deactivate it.
        2. Override the locale with
        """

        with translation.override('de', deactivate=True):
            t = Template("{{ _('No') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    def test_multiple_locale_direct_switch(self):
        with translation.override('de'):
            t = Template("{{ _('No') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    # Literal marked up with _(), loading the i18n template tag library

    def test_multiple_locale_loadi18n(self):
        with translation.override('de'):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override(self._old_language), translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    def test_multiple_locale_loadi18n_deactivate(self):
        """
        Tests the behavior of loading the i18n tag with a specific locale and then overriding it to a different locale. The function first sets the locale to 'de' and deactivates it, then loads the i18n tag in a template. It then switches the locale to 'nl' and checks if the rendered template output is 'Nee' (which is the Dutch translation of 'No').
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Temp
        """

        with translation.override('de', deactivate=True):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    def test_multiple_locale_loadi18n_direct_switch(self):
        with translation.override('de'):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')


class I18nStringLiteralTests(SimpleTestCase):
    """translation of constant strings"""
    libraries = {'i18n': 'django.templatetags.i18n'}

    @setup({'i18n13': '{{ _("Password") }}'})
    def test_i18n13(self):

        with translation.override('de'):
            output = self.engine.render_to_string('i18n13')
        self.assertEqual(output, 'Passwort')

    @setup({'i18n14': '{% cycle "foo" _("Password") _(\'Password\') as c %} {% cycle c %} {% cycle c %}'})
    def test_i18n14(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n14')
        self.assertEqual(output, 'foo Passwort Passwort')

    @setup({'i18n15': '{{ absent|default:_("Password") }}'})
    def test_i18n15(self):
        """
        Tests the translation of a string in a template using Django's translation.override context manager.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - translation.override('de'): A context manager used to temporarily set the Django translation to German ('de').
        
        Input:
        - A template with the variable 'absent' set to an empty string.
        
        Output:
        - The translated string 'Passwort' as a result of the template rendering process.
        """

        with translation.override('de'):
            output = self.engine.render_to_string('i18n15', {'absent': ''})
        self.assertEqual(output, 'Passwort')

    @setup({'i18n16': '{{ _("<") }}'})
    def test_i18n16(self):
        """
        Tests the i18n16 template tag with German language override.
        
        This function overrides the current language to German ('de') and then renders the 'i18n16' template to a string. The expected output is '<'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The function uses Django's translation.override context manager to set the language.
        - The 'i18n16' template is rendered using the engine's render_to_string method.
        """

        with translation.override('de'):
            output = self.engine.render_to_string('i18n16')
        self.assertEqual(output, '<')
