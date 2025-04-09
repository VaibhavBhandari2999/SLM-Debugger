"""
The provided Python file contains unit tests for the `truncatewords` filter in Django templates. It includes tests for both template tags and standalone functions. The `TruncatewordsTests` class contains tests for the `truncatewords` template tag, which truncates a string to a specified number of words, handling both regular strings and marked safe strings. The `FunctionTests` class contains tests for the `truncatewords` function, which performs similar functionality but operates on plain strings rather than template contexts. Both sets of tests ensure that the truncation logic works correctly, handles edge cases like invalid inputs, and properly replaces truncated parts with an ellipsis. The tests cover various scenarios including different lengths of input strings, handling of HTML entities, and truncation based
"""
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
        Truncates a string to a specified number of words, handling both regular strings and marked safe strings. The function uses the `render_to_string` method from the engine to render the template 'truncatewords01' with the provided context. It then compares the rendered output to an expected result using the `assertEqual` method.
        
        Args:
        self: The instance of the class containing this method.
        
        Returns:
        None
        
        Important Functions:
        - `render_to_string`: Renders
        """

        output = self.engine.render_to_string(
            'truncatewords01', {'a': 'alpha & bravo', 'b': mark_safe('alpha &amp; bravo')}
        )
        self.assertEqual(output, 'alpha & … alpha &amp; …')

    @setup({'truncatewords02': '{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}'})
    def test_truncatewords02(self):
        """
        Truncates the given text to a specified length, ensuring that HTML entities are properly handled. The function takes a template context with two variables: 'a' and 'b'. Variable 'a' contains plain text, while 'b' contains marked safe HTML text. The engine renders the 'truncatewords02' template using these variables and truncates both texts to fit within a certain character limit, replacing the truncated parts with an ellipsis. The expected output is a string where both 'a
        """

        output = self.engine.render_to_string(
            'truncatewords02', {'a': 'alpha & bravo', 'b': mark_safe('alpha &amp; bravo')}
        )
        self.assertEqual(output, 'alpha &amp; … alpha &amp; …')


class FunctionTests(SimpleTestCase):

    def test_truncate(self):
        self.assertEqual(truncatewords('A sentence with a few words in it', 1), 'A …')

    def test_truncate2(self):
        """
        Truncate a given sentence to a specified number of words, appending an ellipsis if the original sentence is longer than the specified word count.
        
        Args:
        sentence (str): The input sentence to be truncated.
        word_count (int): The maximum number of words allowed in the truncated sentence.
        
        Returns:
        str: The truncated sentence with an ellipsis if necessary.
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 5),
            'A sentence with a few …',
        )

    def test_overtruncate(self):
        """
        Truncate a sentence to a specified number of words.
        
        Args:
        sentence (str): The input sentence to be truncated.
        
        Returns:
        str: The truncated sentence if the original sentence has more than 100 words, otherwise returns the original sentence.
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 100),
            'A sentence with a few words in it',
        )

    def test_invalid_number(self):
        """
        Truncate a sentence to a specified number of words.
        
        Args:
        sentence (str): The input sentence to be truncated.
        num_words (int): The number of words to truncate the sentence to.
        
        Returns:
        str: The truncated sentence.
        
        Raises:
        ValueError: If `num_words` is not an integer.
        
        Example:
        >>> truncatewords('A sentence with a few words in it', 5)
        'A sentence with a few'
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
