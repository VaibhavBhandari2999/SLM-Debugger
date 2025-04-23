from django.test import SimpleTestCase

from ..utils import SafeClass, UnsafeClass, setup


class AutoescapeStringfilterTests(SimpleTestCase):
    """
    Filters decorated with stringfilter still respect is_safe.
    """

    @setup({"autoescape-stringfilter01": "{{ unsafe|capfirst }}"})
    def test_autoescape_stringfilter01(self):
        """
        Tests the autoescape behavior for a string filter. The function takes a template context with a dictionary containing a single key 'unsafe', which maps to an instance of the UnsafeClass. The UnsafeClass is expected to contain a method that returns a string with special characters that should be escaped. The function renders the template and returns the output, which is then compared to the expected result "You &amp; me".
        
        Parameters:
        - self: The test case instance (unittest.TestCase).
        
        Returns:
        - str:
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
        Tests the autoescaping behavior of a string filter in a template rendering context. The function takes a template named 'autoescape-stringfilter04' and a context variable 'safe' of type SafeClass. The SafeClass is expected to contain a string with an HTML entity. The function renders the template with the provided context and asserts that the output is "You &gt; me", where the greater-than sign is properly escaped.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter04", {"safe": SafeClass()}
        )
        self.assertEqual(output, "You &gt; me")
