from django.test import SimpleTestCase

from ..utils import setup


class InvalidStringTests(SimpleTestCase):
    libraries = {'i18n': 'django.templatetags.i18n'}

    @setup({'invalidstr01': '{{ var|default:"Foo" }}'})
    def test_invalidstr01(self):
        output = self.engine.render_to_string('invalidstr01')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, 'Foo')

    @setup({'invalidstr02': '{{ var|default_if_none:"Foo" }}'})
    def test_invalidstr02(self):
        """
        Tests rendering a template with an invalid string.
        
        This function tests the rendering of a template named 'invalidstr02'. It checks if the engine renders the template correctly based on the `string_if_invalid` setting. If `string_if_invalid` is set, the function expects the output to be 'INVALID'. Otherwise, it expects an empty string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Note:
        The test assumes the existence of an `engine` object with a `render_to_string
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
        """
        Tests the rendering of a template with an invalid string. If the engine's `string_if_invalid` attribute is set, the output should be 'INVALID'. Otherwise, the output should be an empty string.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Attributes:
        - `engine`: The template engine being tested.
        - `string_if_invalid`: A boolean attribute of the template engine indicating whether to return a default string for invalid templates.
        """

        output = self.engine.render_to_string('invalidstr06')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'invalidstr07': '{% load i18n %}{% blocktranslate %}{{ var }}{% endblocktranslate %}'})
    def test_invalidstr07(self):
        output = self.engine.render_to_string('invalidstr07')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')
