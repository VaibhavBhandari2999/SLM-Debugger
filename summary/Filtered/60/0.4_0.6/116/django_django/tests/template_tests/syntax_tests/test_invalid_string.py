from django.test import SimpleTestCase

from ..utils import setup


class InvalidStringTests(SimpleTestCase):
    libraries = {"i18n": "django.templatetags.i18n"}

    @setup({"invalidstr01": '{{ var|default:"Foo" }}'})
    def test_invalidstr01(self):
        """
        Tests the behavior of the template engine when rendering a template with an invalid string. The function `test_invalidstr01` checks how the engine handles invalid strings in templates. It renders the template "invalidstr01" and compares the output to either "INVALID" or "Foo" based on the `string_if_invalid` setting. If `string_if_invalid` is set, the output should be "INVALID"; otherwise, it should be "Foo".
        
        :returns: None
        :rtype:
        """

        output = self.engine.render_to_string("invalidstr01")
        if self.engine.string_if_invalid:
            self.assertEqual(output, "INVALID")
        else:
            self.assertEqual(output, "Foo")

    @setup({"invalidstr02": '{{ var|default_if_none:"Foo" }}'})
    def test_invalidstr02(self):
        output = self.engine.render_to_string("invalidstr02")
        if self.engine.string_if_invalid:
            self.assertEqual(output, "INVALID")
        else:
            self.assertEqual(output, "")

    @setup({"invalidstr03": "{% for v in var %}({{ v }}){% endfor %}"})
    def test_invalidstr03(self):
        output = self.engine.render_to_string("invalidstr03")
        self.assertEqual(output, "")

    @setup({"invalidstr04": "{% if var %}Yes{% else %}No{% endif %}"})
    def test_invalidstr04(self):
        output = self.engine.render_to_string("invalidstr04")
        self.assertEqual(output, "No")

    @setup({"invalidstr04_2": '{% if var|default:"Foo" %}Yes{% else %}No{% endif %}'})
    def test_invalidstr04_2(self):
        output = self.engine.render_to_string("invalidstr04_2")
        self.assertEqual(output, "Yes")

    @setup({"invalidstr05": "{{ var }}"})
    def test_invalidstr05(self):
        output = self.engine.render_to_string("invalidstr05")
        if self.engine.string_if_invalid:
            self.assertEqual(output, "INVALID")
        else:
            self.assertEqual(output, "")

    @setup({"invalidstr06": "{{ var.prop }}"})
    def test_invalidstr06(self):
        output = self.engine.render_to_string("invalidstr06")
        if self.engine.string_if_invalid:
            self.assertEqual(output, "INVALID")
        else:
            self.assertEqual(output, "")

    @setup(
        {
            "invalidstr07": (
                "{% load i18n %}{% blocktranslate %}{{ var }}{% endblocktranslate %}"
            )
        }
    )
    def test_invalidstr07(self):
        output = self.engine.render_to_string("invalidstr07")
        if self.engine.string_if_invalid:
            self.assertEqual(output, "INVALID")
        else:
            self.assertEqual(output, "")
