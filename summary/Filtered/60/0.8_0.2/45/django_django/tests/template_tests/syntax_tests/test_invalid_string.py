from django.test import SimpleTestCase

from ..utils import setup


class InvalidStringTests(SimpleTestCase):
    libraries = {'i18n': 'django.templatetags.i18n'}

    @setup({'invalidstr01': '{{ var|default:"Foo" }}'})
    def test_invalidstr01(self):
        """
        Tests the behavior of the template engine when rendering a template with an invalid string. If the engine's `string_if_invalid` attribute is set, the output should be 'INVALID'. Otherwise, the output should be 'Foo'. The test does not take any parameters and does not return anything.
        
        Key Attributes:
        - `engine`: The template engine instance being tested.
        - `string_if_invalid`: A boolean attribute of the template engine that determines the output when an invalid string is encountered.
        
        Expected Outputs:
        -
        """

        output = self.engine.render_to_string('invalidstr01')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, 'Foo')

    @setup({'invalidstr02': '{{ var|default_if_none:"Foo" }}'})
    def test_invalidstr02(self):
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
        Tests the behavior of the template engine when rendering a template that contains an invalid string. The test checks whether the engine returns 'INVALID' when the `string_if_invalid` setting is enabled, and an empty string when it is disabled.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This is a test method that asserts expected behavior rather than returning a value.
        
        Key Points:
        - The test uses `render_to_string` method of the template engine.
        - The template being tested
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
