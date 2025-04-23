from django.template.defaultfilters import slugify
from django.test import SimpleTestCase
from django.utils.functional import lazy
from django.utils.safestring import mark_safe

from ..utils import setup


class SlugifyTests(SimpleTestCase):
    """
    Running slugify on a pre-escaped string leads to odd behavior,
    but the result is still safe.
    """

    @setup(
        {
            "slugify01": (
                "{% autoescape off %}{{ a|slugify }} {{ b|slugify }}{% endautoescape %}"
            )
        }
    )
    def test_slugify01(self):
        """
        Tests the slugify functionality in the template engine.
        
        This function renders a template named 'slugify01' with two variables: 'a' and 'b'. Variable 'a' contains the string "a & b", and variable 'b' contains the string "a &amp; b" marked as safe. The function then compares the rendered output to the expected string "a-b a-amp-b".
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: The function
        """

        output = self.engine.render_to_string(
            "slugify01", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "a-b a-amp-b")

    @setup({"slugify02": "{{ a|slugify }} {{ b|slugify }}"})
    def test_slugify02(self):
        """
        Tests the slugify functionality with different inputs.
        
        This function tests the slugify method by rendering a template with two parameters: 'a' and 'b'. The parameter 'a' is a string containing special characters, and 'b' is a string with HTML-escaped special characters. The expected output is a slugified version of the input strings, where special characters are replaced with hyphens.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - a (str): A
        """

        output = self.engine.render_to_string(
            "slugify02", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "a-b a-amp-b")


class FunctionTests(SimpleTestCase):
    def test_slugify(self):
        self.assertEqual(
            slugify(
                " Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/"
            ),
            "jack-jill-like-numbers-123-and-4-and-silly-characters",
        )

    def test_unicode(self):
        self.assertEqual(
            slugify("Un \xe9l\xe9phant \xe0 l'or\xe9e du bois"),
            "un-elephant-a-loree-du-bois",
        )

    def test_non_string_input(self):
        self.assertEqual(slugify(123), "123")

    def test_slugify_lazy_string(self):
        """
        Tests the slugify function with a lazy string input.
        
        Args:
        lazy_str (lazy string): A lazy string that returns a string when called.
        
        Returns:
        None: The function asserts the expected output, so it does not return any value.
        
        Key Parameters:
        - lazy_str: A lazy string that is evaluated to a string containing various characters including spaces, punctuation, and special characters.
        
        Expected Output:
        The function checks if the slugified version of the lazy string's evaluated value matches the
        """

        lazy_str = lazy(lambda string: string, str)
        self.assertEqual(
            slugify(
                lazy_str(
                    " Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/"
                )
            ),
            "jack-jill-like-numbers-123-and-4-and-silly-characters",
        )
