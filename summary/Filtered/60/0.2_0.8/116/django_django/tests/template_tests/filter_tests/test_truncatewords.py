from django.template.defaultfilters import truncatewords
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class TruncatewordsTests(SimpleTestCase):
    @setup(
        {
            "truncatewords01": (
                '{% autoescape off %}{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}'
                "{% endautoescape %}"
            )
        }
    )
    def test_truncatewords01(self):
        """
        Tests the truncatewords filter in a template context.
        
        This function tests the `truncatewords` filter with two different inputs:
        - `a`: A string containing special characters and spaces.
        - `b`: A string containing special characters and spaces, marked as safe to prevent HTML escaping.
        
        The function renders the template `truncatewords01` with these inputs and checks if the output is as expected.
        
        Parameters:
        - `self`: The test case instance.
        
        Returns:
        - None: The function asserts the expected
        """

        output = self.engine.render_to_string(
            "truncatewords01",
            {"a": "alpha & bravo", "b": mark_safe("alpha &amp; bravo")},
        )
        self.assertEqual(output, "alpha & … alpha &amp; …")

    @setup({"truncatewords02": '{{ a|truncatewords:"2" }} {{ b|truncatewords:"2"}}'})
    def test_truncatewords02(self):
        output = self.engine.render_to_string(
            "truncatewords02",
            {"a": "alpha & bravo", "b": mark_safe("alpha &amp; bravo")},
        )
        self.assertEqual(output, "alpha &amp; … alpha &amp; …")


class FunctionTests(SimpleTestCase):
    def test_truncate(self):
        self.assertEqual(truncatewords("A sentence with a few words in it", 1), "A …")

    def test_truncate2(self):
        """
        Truncate a sentence to a specified number of words and append an ellipsis if the sentence is longer than the specified length.
        
        Parameters:
        sentence (str): The input sentence to be truncated.
        num_words (int): The maximum number of words to include in the truncated sentence.
        
        Returns:
        str: The truncated sentence with an ellipsis if it was longer than the specified number of words, otherwise the original sentence.
        """

        self.assertEqual(
            truncatewords("A sentence with a few words in it", 5),
            "A sentence with a few …",
        )

    def test_overtruncate(self):
        self.assertEqual(
            truncatewords("A sentence with a few words in it", 100),
            "A sentence with a few words in it",
        )

    def test_invalid_number(self):
        self.assertEqual(
            truncatewords("A sentence with a few words in it", "not a number"),
            "A sentence with a few words in it",
        )

    def test_non_string_input(self):
        self.assertEqual(truncatewords(123, 2), "123")
