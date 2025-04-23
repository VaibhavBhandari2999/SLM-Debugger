from django.test import SimpleTestCase

from ..utils import SafeClass, UnsafeClass, setup


class AutoescapeStringfilterTests(SimpleTestCase):
    """
    Filters decorated with stringfilter still respect is_safe.
    """

    @setup({"autoescape-stringfilter01": "{{ unsafe|capfirst }}"})
    def test_autoescape_stringfilter01(self):
        """
        Tests the autoescaping behavior for a string filter in a template rendering context. The function takes a template named 'autoescape-stringfilter01' and a dictionary containing an instance of `UnsafeClass` with a method `render` that returns a string with special characters. The function renders the template with the provided context and asserts that the output is "You &amp; me", demonstrating proper autoescaping of the special characters.
        Parameters:
        None
        
        Returns:
        None
        
        Key Behavior:
        -
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter01", {"unsafe": UnsafeClass()}
        )
        self.assertEqual(output, "You &amp; me")

    @setup(
        {
            "autoescape-stringfilter02": (
                "{% autoescape off %}{{ unsafe|capfirst }}{% endautoescape %}"
            )
        }
    )
    def test_autoescape_stringfilter02(self):
        output = self.engine.render_to_string(
            "autoescape-stringfilter02", {"unsafe": UnsafeClass()}
        )
        self.assertEqual(output, "You & me")

    @setup({"autoescape-stringfilter03": "{{ safe|capfirst }}"})
    def test_autoescape_stringfilter03(self):
        output = self.engine.render_to_string(
            "autoescape-stringfilter03", {"safe": SafeClass()}
        )
        self.assertEqual(output, "You &gt; me")

    @setup(
        {
            "autoescape-stringfilter04": (
                "{% autoescape off %}{{ safe|capfirst }}{% endautoescape %}"
            )
        }
    )
    def test_autoescape_stringfilter04(self):
        """
        Tests the autoescaping behavior of a string filter in a template rendering context.
        
        Args:
        safe (SafeClass): An instance of SafeClass used to test the autoescaping of the string filter.
        
        Returns:
        str: The rendered output of the template, which should be "You &gt; me" due to the autoescaping of the '>' character.
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter04", {"safe": SafeClass()}
        )
        self.assertEqual(output, "You &gt; me")
