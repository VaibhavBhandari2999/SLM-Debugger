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
        Truncate a string to a specified number of words while preserving HTML tags.
        
        Args:
        text (str): The input string containing HTML content.
        num_words (int): The maximum number of words to include in the truncated string.
        
        Returns:
        str: The truncated string with HTML tags preserved and an ellipsis appended if truncation occurred.
        
        Example:
        >>> truncatewords_html('<p>one <a href="#">two - three <br>four</a> five</p>', 2
        """

        self.assertEqual(
            truncatewords_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 2
            ),
            '<p>one <a href="#">two …</a></p>',
        )

    def test_truncate2(self):
        """
        Truncate a string to a specified number of words while preserving HTML tags.
        
        Args:
        text (str): The input string containing HTML content.
        num_words (int): The maximum number of words to include in the output.
        
        Returns:
        str: The truncated string with HTML tags preserved up to the specified word count, followed by an ellipsis if truncated.
        
        Example:
        >>> truncatewords_html('<p>one <a href="#">two - three <br>four</a> five</
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
elf.assertEqual(
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
