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
        Tests the functionality of the 'yesno' filter with multiple locale settings.
        
        This function checks the 'yesno' filter behavior when the template is rendered
        with different locale settings. It first sets the locale to 'de' and then
        renders a template with the 'yesno' filter. After that, it temporarily overrides
        the locale to 'nl' to check the filter's output.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Overrides the current locale to '
        """

        with translation.override('de'):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override(self._old_language), translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    def test_multiple_locale_filter_deactivate(self):
        """
        Tests the behavior of the `yesno` filter in a Django template when multiple locale settings are used.
        
        This test function checks how the `yesno` filter behaves when the 'de' locale is temporarily overridden with `deactivate=True`, and then the 'nl' locale is used for rendering the template. The function expects the template to render 'nee' when the 'nl' locale is active, as 'nee' is the Dutch translation for 'no'.
        
        Parameters:
        - None
        
        Returns:
        """

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
        Test the i18n14 template with German language override.
        
        This function tests the rendering of the 'i18n14' template with the 'de' (German) language override. It uses Django's translation context to set the language to German during the template rendering process. The expected output is compared against the actual output to ensure that the template correctly handles the language override, particularly in relation to password-related text.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
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
        """
        Tests the i18n16 template tag with German language override.
        
        This function renders the 'i18n16' template with the 'de' language override and checks if the output is '<'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Use Django's translation.override context manager to set the language to 'de' (German).
        2. Render the 'i18n16' template using the template engine.
        3. Assert that the rendered output
        """

        with translation.override('de'):
            output = self.engine.render_to_string('i18n16')
        self.assertEqual(output, '<')
