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

    @setup({'slugify01': '{% autoescape off %}{{ a|slugify }} {{ b|slugify }}{% endautoescape %}'})
    def test_slugify01(self):
        output = self.engine.render_to_string('slugify01', {'a': 'a & b', 'b': mark_safe('a &amp; b')})
        self.assertEqual(output, 'a-b a-amp-b')

    @setup({'slugify02': '{{ a|slugify }} {{ b|slugify }}'})
    def test_slugify02(self):
        output = self.engine.render_to_string('slugify02', {'a': 'a & b', 'b': mark_safe('a &amp; b')})
        self.assertEqual(output, 'a-b a-amp-b')


class FunctionTests(SimpleTestCase):

    def test_slugify(self):
        """
        Test the slugify function.
        
        This test checks if the slugify function correctly converts a given string into a slug. The input string may contain spaces, punctuation, and special characters. The function should remove these and replace them with hyphens, ensuring the resulting slug is all lowercase.
        
        Parameters:
        None (the test function does not take any parameters).
        
        Returns:
        None (the test function does not return anything, it asserts the expected result).
        
        Example:
        >>> slugify(' Jack & Jill
        """

        self.assertEqual(
            slugify(' Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/'),
            'jack-jill-like-numbers-123-and-4-and-silly-characters',
        )

    def test_unicode(self):
        self.assertEqual(
            slugify("Un \xe9l\xe9phant \xe0 l'or\xe9e du bois"),
            'un-elephant-a-loree-du-bois',
        )

    def test_non_string_input(self):
        self.assertEqual(slugify(123), '123')

    def test_slugify_lazy_string(self):
        lazy_str = lazy(lambda string: string, str)
        self.assertEqual(
            slugify(lazy_str(' Jack & Jill like numbers 1,2,3 and 4 and silly characters ?%.$!/')),
            'jack-jill-like-numbers-123-and-4-and-silly-characters',
        )
