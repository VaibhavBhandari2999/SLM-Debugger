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
        
        This function renders a template with two variables: 'a' and 'b'. Variable 'a' contains the string 'alpha & bravo', while 'b' contains the same string but with HTML entities properly escaped using mark_safe. The function then compares the rendered output to the expected result, 'alpha & … alpha &amp; …'.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: The function asserts the expected output and
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
        self.assertEqual(
            truncatewords('A sentence with a few words in it', 100),
            'A sentence with a few words in it',
        )

    def test_invalid_number(self):
        """
        Test the truncatewords function with an invalid number of words.
        
        Args:
        sentence (str): The sentence to truncate.
        num_words (int): The number of words to truncate to.
        
        Returns:
        str: The truncated sentence.
        
        Raises:
        TypeError: If num_words is not an integer.
        """

        self.assertEqual(
            truncatewords('A sentence with a few words in it', 'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
'not a number'),
            'A sentence with a few words in it',
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), '123')
