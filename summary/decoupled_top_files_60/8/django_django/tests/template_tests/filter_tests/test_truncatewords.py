from django.template.defaultfilters import truncatewords
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class TruncatewordsTests(SimpleTestCase):

    @setup({
        'truncatewords01': '{% autoescape off %}{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}{% endautoescape %}'
    })
    def test_truncatewords01(self):
        """
        Tests the truncatewords01 template filter.
        
        This function renders the 'truncatewords01' template with two context variables:
        - 'a': a string containing 'alpha & bravo'
        - 'b': a string containing 'alpha &amp; bravo' marked as safe
        
        The expected output is a truncated version of the strings, with '…' indicating the truncation point.
        The function asserts that the rendered output matches the expected result: 'alpha & … alpha &amp; …'.
        """

        output = self.engine.render_to_string(
            'truncatewords01', {'a': 'alpha & bravo', 'b': mark_safe('alpha &amp; bravo')}
        )
        self.assertEqual(output, 'alpha & … alpha &amp; …')

    @setup({'truncatewords02': '{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}'})
    def test_truncatewords02(self):
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
        """
        Truncate a sentence to a specified number of words.
        
        Args:
        sentence (str): The sentence to be truncated.
        word_limit (int): The maximum number of words allowed in the truncated sentence.
        
        Returns:
        str: The truncated sentence, which will be the original sentence if it is shorter than the word limit.
        
        Example:
        >>> truncatewords('A sentence with a few words in it', 100)
        'A sentence with a few words in it'
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 100),
            'A sentence with a few words in it',
        )

    def test_invalid_number(self):
        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
