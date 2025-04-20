from django.template.defaultfilters import truncatewords
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class TruncatewordsTests(SimpleTestCase):

    @setup({
        'truncatewords01': '{% autoescape off %}{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}{% endautoescape %}'
    })
    def test_truncatewords01(self):
        output = self.engine.render_to_string(
            'truncatewords01', {'a': 'alpha & bravo', 'b': mark_safe('alpha &amp; bravo')}
        )
        self.assertEqual(output, 'alpha & … alpha &amp; …')

    @setup({'truncatewords02': '{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}'})
    def test_truncatewords02(self):
        """
        Tests the behavior of the `truncatewords` template filter with different inputs.
        
        This function renders a template with two variables: 'a' and 'b'. Variable 'a' contains the string 'alpha & bravo', while 'b' contains the same string but with HTML-escaped ampersands. The `truncatewords` filter is applied to both variables, and the output is expected to be 'alpha &amp; … alpha &amp; …'.
        
        Parameters:
        - self: The test case
        """

        output = self.engine.render_to_string(
            'truncatewords02', {'a': 'alpha & bravo', 'b': mark_safe('alpha &amp; bravo')}
        )
        self.assertEqual(output, 'alpha &amp; … alpha &amp; …')


class FunctionTests(SimpleTestCase):

    def test_truncate(self):
        self.assertEqual(truncatewords('A sentence with a few words in it', 1), 'A …')

    def test_truncate2(self):
        self.assertEqual(
            truncatewords('A sentence with a few words in it', 5),
            'A sentence with a few …',
        )

    def test_overtruncate(self):
        self.assertEqual(
            truncatewords('A sentence with a few words in it', 100),
            'A sentence with a few words in it',
        )

    def test_invalid_number(self):
        """
        Truncate a sentence to a specified number of words.
        
        Args:
        sentence (str): The sentence to be truncated.
        num_words (int): The number of words to truncate the sentence to.
        
        Returns:
        str: The truncated sentence.
        
        Raises:
        ValueError: If the input 'num_words' is not a valid integer.
        
        Example:
        >>> truncatewords('A sentence with a few words in it', 5)
        'A sentence with a few words in it'
        >>> truncate
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
