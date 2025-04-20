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
        
        This function tests the behavior of the 'truncatewords01' template filter with two different inputs:
        - 'a': A string containing 'alpha & bravo'.
        - 'b': A string containing 'alpha &amp; bravo' with the mark_safe function applied to it.
        
        The function renders the template 'truncatewords01' with these inputs and checks if the output matches the expected result, which is 'alpha & … alpha &amp;
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
        sentence (str): The input sentence to be truncated.
        max_words (int): The maximum number of words allowed in the truncated sentence.
        
        Returns:
        str: The truncated sentence, which will be the original sentence if it is shorter than or equal to the specified number of words.
        """

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
        TypeError: If num_words is not an integer.
        
        Example:
        >>> truncatewords('A sentence with a few words in it', 3)
        'A sentence with a few'
        >>> truncatewords('A sentence with a few words
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
