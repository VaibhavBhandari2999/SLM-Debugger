from django.template.defaultfilters import truncatewords_html
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_truncate_zero(self):
        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 0
            ),
            "",
        )

    def test_truncate(self):
        """
        Truncate a given HTML string to a specified number of words.
        
        Args:
        html_string (str): The HTML string to be truncated.
        num_words (int): The maximum number of words to include in the truncated string.
        
        Returns:
        str: The truncated HTML string with an ellipsis indicating truncation.
        
        Example:
        >>> truncatewords_html('<p>one <a href="#">two - three <br>four</a> five</p>', 2)
        '<p>one
        """

        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 2
            ),
            '<p>one <a href="#">two …</a></p>',
        )

    def test_truncate2(self):
        """
        Truncate a string containing HTML to a specified number of words, ensuring that the truncation does not cut off a word in the middle. The function takes an HTML string and a number of words as input and returns a truncated version of the string. If the truncation occurs within a tag, the tag is closed properly. The function handles HTML tags and ensures that the output is still valid HTML.
        
        Parameters:
        html_string (str): The HTML string to be truncated.
        num_words (int
        """

        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 4
            ),
            '<p>one <a href="#">two - three …</a></p>',
        )

    def test_truncate3(self):
        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 5
            ),
            '<p>one <a href="#">two - three <br>four …</a></p>',
        )

    def test_truncate4(self):
        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 100
            ),
            '<p>one <a href="#">two - three <br>four</a> five</p>',
        )

    def test_truncate_unicode(self):
        """
        Truncate a Unicode string to a specified number of words, replacing the end with an ellipsis if the original string exceeds the specified word count.
        
        Parameters:
        text (str): The Unicode string to be truncated.
        word_count (int): The maximum number of words to include in the truncated string.
        
        Returns:
        str: The truncated string, with an ellipsis appended if the original string exceeded the specified word count.
        
        Example:
        >>> truncatewords_html("\xc5ngstr\xf6
        """

        self.assertEqual(
            truncatewords_html("\xc5ngstr\xf6m was here", 1), "\xc5ngstr\xf6m …"
        )

    def test_truncate_complex(self):
        self.assertEqual(
            truncatewords_html(
                "<i>Buenos d&iacute;as! &#x00bf;C&oacute;mo est&aacute;?</i>", 3
            ),
            "<i>Buenos d&iacute;as! &#x00bf;C&oacute;mo …</i>",
        )

    def test_invalid_arg(self):
        self.assertEqual(truncatewords_html("<p>string</p>", "a"), "<p>string</p>")
