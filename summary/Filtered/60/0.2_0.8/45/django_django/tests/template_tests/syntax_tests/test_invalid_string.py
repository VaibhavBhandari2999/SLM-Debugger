from django.test import SimpleTestCase

from ..utils import setup


class InvalidStringTests(SimpleTestCase):
    libraries = {'i18n': 'django.templatetags.i18n'}

    @setup({'invalidstr01': '{{ var|default:"Foo" }}'})
    def test_invalidstr01(self):
        """
        Tests the behavior of the render_to_string method when an invalid string template is provided.
        
        Parameters:
        - self: The instance of the test case.
        
        Returns:
        - The rendered output of the template, which should be 'INVALID' if string_if_invalid is set, otherwise 'Foo'.
        """

        output = self.engine.render_to_string('invalidstr01')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, 'Foo')

    @setup({'invalidstr02': '{{ var|default_if_none:"Foo" }}'})
    def test_invalidstr02(self):
        """
        Tests the rendering of an invalid string template.
        
        This function tests the behavior of the `render_to_string` method when provided with an invalid template string. The test checks if the output is either the string specified by `string_if_invalid` or an empty string, depending on the configuration.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Behavior:
        - If `string_if_invalid` is set, the output should be 'INVALID'.
        - If `string_if_invalid` is not set, the output
        """

        output = self.engine.render_to_string('invalidstr02')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'invalidstr03': '{% for v in var %}({{ v }}){% endfor %}'})
    def test_invalidstr03(self):
        output = self.engine.render_to_string('invalidstr03')
        self.assertEqual(output, '')

    @setup({'invalidstr04': '{% if var %}Yes{% else %}No{% endif %}'})
    def test_invalidstr04(self):
        output = self.engine.render_to_string('invalidstr04')
        self.assertEqual(output, 'No')

    @setup({'invalidstr04_2': '{% if var|default:"Foo" %}Yes{% else %}No{% endif %}'})
    def test_invalidstr04_2(self):
        output = self.engine.render_to_string('invalidstr04_2')
        self.assertEqual(output, 'Yes')

    @setup({'invalidstr05': '{{ var }}'})
    def test_invalidstr05(self):
        output = self.engine.render_to_string('invalidstr05')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'invalidstr06': '{{ var.prop }}'})
    def test_invalidstr06(self):
        output = self.engine.render_to_string('invalidstr06')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'invalidstr07': '{% load i18n %}{% blocktranslate %}{{ var }}{% endblocktranslate %}'})
    def test_invalidstr07(self):
        """
        Tests rendering a template with an invalid string.
        
        This function tests the rendering of a template with an invalid string. It checks whether the output is either the string 'INVALID' if `string_if_invalid` is set, or an empty string if `string_if_invalid` is not set.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - engine: The template engine instance used for rendering.
        - string_if_invalid: A boolean indicating whether to use a default string for invalid templates.
        """

        output = self.engine.render_to_string('invalidstr07')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')
