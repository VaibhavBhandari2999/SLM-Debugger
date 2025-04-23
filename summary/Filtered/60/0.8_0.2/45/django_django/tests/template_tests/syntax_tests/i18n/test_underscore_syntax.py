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
        Tests the behavior of the 'yesno' filter in Django templates with multiple locale overrides.
        
        This function checks how the 'yesno' filter behaves when the template is rendered with different locales. It first sets the locale to 'de' (German) and then uses the 'yesno' filter with the provided choices in German. After that, it temporarily overrides the locale to 'nl' (Dutch) and checks the output of the rendered template.
        
        Parameters:
        - None
        
        Returns:
        - None
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
        """
        Tests the behavior of the 'yesno' filter in Django templates when the locale is switched directly.
        
        This function checks the 'yesno' filter in a Django template with different locales. It first sets the locale to 'de' (German) and renders a template with the 'yesno' filter using the provided German translation strings. Then, it switches the locale to 'nl' (Dutch) and asserts that the rendered output is 'nee', which is the Dutch translation for 'no'.
        """

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
        with translation.override('de', deactivate=True):
            t = Template("{% load i18n %}{{ _('No') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'Nee')

    def test_multiple_locale_loadi18n_direct_switch(self):
        """
        Test the behavior of loading the i18n tag and switching locales directly in a Django template.
        
        This function checks that when the 'de' locale is set, the template loads the i18n tag and renders the German word for 'No'. Then, when the 'nl' locale is set, it ensures that the template renders the Dutch word for 'No' instead.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Use `translation.override('de')`
        """

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
        """
        Tests the i18n14 template tag with German language override.
        
        Parameters:
        None
        
        Input:
        - No explicit input parameters.
        - The test uses a template 'i18n14' which contains text to be translated.
        
        Output:
        - A string output from rendering the template with 'de' language override.
        - Expected output: 'foo Passwort Passwort'
        
        This test ensures that the template correctly handles password-related text in German.
        """

        with translation.override('de'):
            output = self.engine.render_to_string('i18n14')
        self.assertEqual(output, 'foo Passwort Passwort')

    @setup({'i18n15': '{{ absent|default:_("Password") }}'})
    def test_i18n15(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n15', {'absent': ''})
        self.assertEqual(output, 'Passwort')

    @setup({'i18n16': '{{ _("<") }}'})
    def test_i18n16(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n16')
        self.assertEqual(output, '<')
output, '<')
