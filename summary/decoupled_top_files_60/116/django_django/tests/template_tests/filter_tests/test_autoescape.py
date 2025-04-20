from django.test import SimpleTestCase

from ..utils import SafeClass, UnsafeClass, setup


class AutoescapeStringfilterTests(SimpleTestCase):
    """
    Filters decorated with stringfilter still respect is_safe.
    """

    @setup({"autoescape-stringfilter01": "{{ unsafe|capfirst }}"})
    def test_autoescape_stringfilter01(self):
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
        """
        Tests the autoescaping behavior for a string filter when applied to an instance of UnsafeClass. The function takes no parameters and returns a string. The UnsafeClass instance passed to the template contains a method that returns a string with special characters. The rendered output should be the string with those characters properly escaped.
        
        Returns:
        str: The rendered template output.
        """

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
        Tests the autoescaping behavior of a string filter in a template context.
        The function takes a template context dictionary with a single key 'safe'
        pointing to an instance of SafeClass. It renders the template 'autoescape-stringfilter04'
        and checks if the output matches the expected string "You &gt; me".
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: The function asserts the expected output and does not return any value.
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter04", {"safe": SafeClass()}
        )
        self.assertEqual(output, "You &gt; me")
