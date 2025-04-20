from django.template.defaultfilters import truncatewords_html
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_truncate_zero(self):
        """
        Truncate a string of HTML content to a specified number of words, with a limit of 0 words.
        
        Parameters:
        html_content (str): The HTML content to be truncated.
        word_limit (int): The maximum number of words to include in the truncated content. A value of 0 means no words should be included.
        
        Returns:
        str: The truncated HTML content as a string.
        
        Example:
        >>> truncatewords_html('<p>one <a href="#">two - three <br
        """

        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 0
            ),
            "",
        )

    def test_truncate(self):
        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 2
            ),
            '<p>one <a href="#">two …</a></p>',
        )

    def test_truncate2(self):
        """
        Truncate a string of HTML content to a specified number of words, ensuring that the truncation does not cut through a word or HTML tag. The function takes two parameters:
        - `html_content`: A string containing HTML content.
        - `word_limit`: An integer specifying the maximum number of words to include in the truncated content.
        
        The function returns a string where the HTML content is truncated to the specified number of words, with an ellipsis ('…') appended if truncation occurs. The truncation
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
        """
        Truncate a given HTML content to a specified number of words.
        
        Args:
        html_content (str): The HTML content to be truncated.
        max_words (int): The maximum number of words to include in the truncated content.
        
        Returns:
        str: The truncated HTML content.
        
        Example:
        >>> truncatewords_html('<p>one <a href="#">two - three <br>four</a> five</p>', 100)
        '<p>one <a href="#">two
        """

        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 100
            ),
            '<p>one <a href="#">two - three <br>four</a> five</p>',
        )

    def test_truncate_unicode(self):
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
, "<p>string</p>")
