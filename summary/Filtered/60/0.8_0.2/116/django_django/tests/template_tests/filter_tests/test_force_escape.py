from django.template.defaultfilters import force_escape
from django.test import SimpleTestCase
from django.utils.safestring import SafeData

from ..utils import setup


class ForceEscapeTests(SimpleTestCase):
    """
    Force_escape is applied immediately. It can be used to provide
    double-escaping, for example.
    """

    @setup(
        {
            "force-escape01": (
                "{% autoescape off %}{{ a|force_escape }}{% endautoescape %}"
            )
        }
    )
    def test_force_escape01(self):
        output = self.engine.render_to_string("force-escape01", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    @setup({"force-escape02": "{{ a|force_escape }}"})
    def test_force_escape02(self):
        output = self.engine.render_to_string("force-escape02", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    @setup(
        {
            "force-escape03": (
                "{% autoescape off %}{{ a|force_escape|force_escape }}"
                "{% endautoescape %}"
            )
        }
    )
    def test_force_escape03(self):
        output = self.engine.render_to_string("force-escape03", {"a": "x&y"})
        self.assertEqual(output, "x&amp;amp;y")

    @setup({"force-escape04": "{{ a|force_escape|force_escape }}"})
    def test_force_escape04(self):
        output = self.engine.render_to_string("force-escape04", {"a": "x&y"})
        self.assertEqual(output, "x&amp;amp;y")

    # Because the result of force_escape is "safe", an additional
    # escape filter has no effect.
    @setup(
        {
            "force-escape05": (
                "{% autoescape off %}{{ a|force_escape|escape }}{% endautoescape %}"
            )
        }
    )
    def test_force_escape05(self):
        output = self.engine.render_to_string("force-escape05", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    @setup({"force-escape06": "{{ a|force_escape|escape }}"})
    def test_force_escape06(self):
        output = self.engine.render_to_string("force-escape06", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    @setup(
        {
            "force-escape07": (
                "{% autoescape off %}{{ a|escape|force_escape }}{% endautoescape %}"
            )
        }
    )
    def test_force_escape07(self):
        output = self.engine.render_to_string("force-escape07", {"a": "x&y"})
        self.assertEqual(output, "x&amp;amp;y")

    @setup({"force-escape08": "{{ a|escape|force_escape }}"})
    def test_force_escape08(self):
        output = self.engine.render_to_string("force-escape08", {"a": "x&y"})
        self.assertEqual(output, "x&amp;amp;y")


class FunctionTests(SimpleTestCase):
    def test_escape(self):
        """
        Tests the `force_escape` function.
        
        This function tests the `force_escape` function, which escapes HTML special characters in a given string. The function takes a single argument:
        - `value` (str): The string containing HTML special characters to be escaped.
        
        The function returns a `SafeData` object, which is a subclass of `str` and is used to mark the string as already escaped.
        
        Example usage:
        ```python
        escaped = force_escape("<some html & special characters > here")
        """

        escaped = force_escape("<some html & special characters > here")
        self.assertEqual(escaped, "&lt;some html &amp; special characters &gt; here")
        self.assertIsInstance(escaped, SafeData)

    def test_unicode(self):
        """
        Test function to escape special characters in a given string.
        
        Args:
        None (this is a test function)
        
        Returns:
        None (this is a test function)
        
        Example:
        >>> test_unicode()
        True
        """

        self.assertEqual(
            force_escape("<some html & special characters > here ĐÅ€£"),
            "&lt;some html &amp; special characters &gt; here \u0110\xc5\u20ac\xa3",
        )
