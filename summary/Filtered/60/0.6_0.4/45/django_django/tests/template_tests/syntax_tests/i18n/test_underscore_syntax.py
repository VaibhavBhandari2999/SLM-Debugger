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
        with translation.override('de'):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override(self._old_language), translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    def test_multiple_locale_filter_deactivate(self):
        """
        Tests the behavior of the `yesno` filter in Django templates when using the `deactivate` option in translation override.
        
        This function checks how the `yesno` filter behaves when the current locale is temporarily deactivated using Django's translation override context manager. Specifically, it overrides the locale to 'de' with `deactivate=True`, then to 'nl', and evaluates the template to ensure that the `yesno` filter returns 'nee' (which means 'no' in Dutch).
        
        Parameters:
        """

        with translation.override('de', deactivate=True):
            t = Template("{% load i18n %}{{ 0|yesno:_('yes,no,maybe') }}")
        with translation.override('nl'):
            self.assertEqual(t.render(Context({})), 'nee')

    def test_multiple_locale_filter_direct_switch(self):
        """
        Tests the behavior of the 'yesno' filter in Django templates when the locale is switched directly.
        
        This function tests the 'yesno' filter in Django templates to ensure that it correctly switches between locales. It first sets the locale to 'de' (German) and renders a template with the 'yesno' filter. Then, it switches the locale to 'nl' (Dutch) and checks that the filter returns the correct localized output.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
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
        """
        Deactivate the German locale and render a template with the Dutch locale.
        
        This function first overrides the current locale with German ('de') and deactivates it, then renders a template with the string 'No' translated to the user's default language. After that, it overrides the locale with Dutch ('nl') and checks if the rendered template returns 'Nee', which is the Dutch translation of 'No'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        None
        
        Note:
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
        """
        Test the i18n13 template function.
        
        This function tests the rendering of the 'i18n13' template with the 'de' language override. It ensures that the output is correctly translated to 'Passwort'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Use Django's translation.override context manager to set the language to 'de'.
        2. Render the 'i18n13' template using the engine.
        3. Assert that the rendered
        """


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
        with translation.override('de'):
            output = self.engine.render_to_string('i18n15', {'absent': ''})
        self.assertEqual(output, 'Passwort')

    @setup({'i18n16': '{{ _("<") }}'})
    def test_i18n16(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n16')
        self.assertEqual(output, '<')
  self.assertEqual(output, '<')
