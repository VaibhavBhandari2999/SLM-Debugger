from django.template.defaultfilters import rjust
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class RjustTests(SimpleTestCase):
    @setup(
        {
            "rjust01": (
                '{% autoescape off %}.{{ a|rjust:"5" }}. .{{ b|rjust:"5" }}.'
                "{% endautoescape %}"
            )
        }
    )
    def test_rjust01(self):
        """
        Tests the rjust method in rendering strings. The function takes a template name and context variables 'a' and 'b'. Variable 'a' is a regular string, while 'b' is a marked safe string. The function renders the template with these variables and checks if the output matches the expected result, which is '.  a&b. .  a&b.'.
        Parameters:
        template_name (str): The name of the template to be rendered.
        context (dict): A
        """

        output = self.engine.render_to_string(
            "rjust01", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, ".  a&b. .  a&b.")

    @setup({"rjust02": '.{{ a|rjust:"5" }}. .{{ b|rjust:"5" }}.'})
    def test_rjust02(self):
        output = self.engine.render_to_string(
            "rjust02", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, ".  a&amp;b. .  a&b.")


class FunctionTests(SimpleTestCase):
    def test_rjust(self):
        self.assertEqual(rjust("test", 10), "      test")

    def test_less_than_string_length(self):
        self.assertEqual(rjust("test", 3), "test")

    def test_non_string_input(self):
        self.assertEqual(rjust(123, 4), " 123")
