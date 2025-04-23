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
        Tests the slugify function with different inputs.
        
        This test function evaluates the slugify function using two different input strings. The first input is a string with special characters, and the second input is a string with HTML-escaped special characters. The function is expected to replace spaces with hyphens and remove special characters, except for the ampersand in the second input, which should be preserved.
        
        Parameters:
        a (str): The first input string containing special characters.
        b (str): The
        """

        output = self.engine.render_to_string(
            "slugify01", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "a-b a-amp-b")

    @setup({"slugify02": "{{ a|slugify }} {{ b|slugify }}"})
    def test_slugify02(self):
        output = self.engine.render_to_string(
            "slugify02", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "a-b a-amp-b")


class FunctionTests(SimpleTestCase):
    def test_slugify(self):
        """
        Tests the slugify function.
        
        Args:
        text (str): The input string to be slugified.
        
        Returns:
        str: The slugified version of the input string.
        """

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
        lazy_str = lazy(lambda string: string, str)
        self.assertEqual(
            slugify(
                lazy_str(
                    " Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/"
                )
            ),
            "jack-jill-like-numbers-123-and-4-and-silly-characters",
        )
