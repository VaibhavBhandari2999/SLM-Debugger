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
        Tests the behavior of the `truncatewords` template filter with different inputs.
        
        This function tests the `truncatewords` template filter by rendering a template with two variables: 'a' and 'b'. Variable 'a' contains the string 'alpha & bravo', while variable 'b' contains the same string but marked as safe HTML using `mark_safe`. The expected output is 'alpha & … alpha &amp; …', where the string is truncated after a certain number of words and the HTML
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
        """
        Truncate a sentence to a specified number of words, appending an ellipsis if the original sentence is longer than the specified length.
        
        Parameters:
        sentence (str): The input sentence to be truncated.
        word_limit (int): The maximum number of words to include in the truncated sentence.
        
        Returns:
        str: The truncated sentence, with an ellipsis appended if the original sentence exceeded the word limit.
        """

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
        Test the truncatewords function with an invalid number argument.
        
        Parameters:
        - sentence (str): The sentence to be truncated.
        - num_words (int): The number of words to truncate to.
        
        Keywords:
        - No additional keywords.
        
        Returns:
        - str: The original sentence if num_words is not a valid integer.
        
        Example:
        >>> truncatewords('A sentence with a few words in it', 'not a number')
        'A sentence with a few words in it'
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
lf.assertEqual(truncatewords(123, 2), '123')
