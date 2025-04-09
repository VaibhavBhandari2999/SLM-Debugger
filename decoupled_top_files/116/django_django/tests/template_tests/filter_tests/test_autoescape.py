from django.test import SimpleTestCase

from ..utils import SafeClass, UnsafeClass, setup


class AutoescapeStringfilterTests(SimpleTestCase):
    """
    Filters decorated with stringfilter still respect is_safe.
    """

    @setup({"autoescape-stringfilter01": "{{ unsafe|capfirst }}"})
    def test_autoescape_stringfilter01(self):
        """
        Tests rendering of a string with an unsafe class using autoescaping and the stringfilter.
        
        Args:
        self: The instance of the test case.
        
        Returns:
        None
        
        Variables:
        output (str): The rendered output string.
        unsafe (UnsafeClass): An instance of the UnsafeClass used as input.
        
        Important Functions:
        - render_to_string: Renders the template with the given context.
        - assertEquals: Compares the expected output with the actual output.
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
        """
        Tests rendering of a string with an unsafe class using autoescaping and the stringfilter.
        
        Args:
        self: The instance of the test case.
        
        Returns:
        None
        
        Variables:
        output (str): The rendered output string.
        unsafe (UnsafeClass): An instance of the UnsafeClass used as input.
        
        Important Functions:
        - render_to_string: Renders the template with the given context.
        - assertEquals: Compares the expected output with the actual output.
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter02", {"unsafe": UnsafeClass()}
        )
        self.assertEqual(output, "You & me")

    @setup({"autoescape-stringfilter03": "{{ safe|capfirst }}"})
    def test_autoescape_stringfilter03(self):
        """
        Tests the rendering of a string with an auto-escaped string filter, where the input is an instance of SafeClass, and the expected output is 'You &gt; me'.
        """

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
        Tests the rendering of a string with an auto-escaped string filter, where the input is an instance of SafeClass, and the expected output is 'You &gt; me'.
        """

        output = self.engine.render_to_string(
            "autoescape-stringfilter04", {"safe": SafeClass()}
        )
        self.assertEqual(output, "You &gt; me")
