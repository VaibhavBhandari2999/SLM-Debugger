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
        Tests the slugify functionality in a template engine.
        
        This function tests the slugify functionality by rendering a template with two variables: 'a' and 'b'. The variable 'a' contains the string "a & b", and 'b' contains the string "a &amp; b" marked as safe. The expected output is a string where both variables are converted to hyphen-separated slugified versions: "a-b a-amp-b".
        
        Parameters:
        - self: The test case instance.
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
        
        Example:
        >>> slugify(" Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/ ")
        'jack-jill-like-numbers-123-and-4-and-silly-characters'
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
        """
        Test the slugify function with a lazy string.
        
        This test checks the slugify function's ability to handle a lazy string that is evaluated to a string containing various characters. The function should convert the string to a slug format, replacing special characters with hyphens and removing spaces.
        
        Parameters:
        lazy_str (lazy object): A lazy string object that evaluates to a string containing alphanumeric characters and special characters.
        
        Returns:
        str: The slugified version of the input string, with special characters replaced by
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
