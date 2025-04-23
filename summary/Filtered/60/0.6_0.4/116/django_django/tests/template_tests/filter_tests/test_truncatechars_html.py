from django.template.defaultfilters import truncatechars_html
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_truncate_zero(self):
        """
        Truncate a given HTML string to a specified number of characters and return the truncated string. If the input string is shorter than the specified number, return the entire string. If the truncation occurs within an HTML tag, the tag is left intact. If the truncation happens at the end of a tag, the tag is closed properly.
        
        Parameters:
        html_str (str): The HTML string to be truncated.
        num_chars (int): The maximum number of characters to include in the truncated string
        """

        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 0
            ),
            "…",
        )

    def test_truncate(self):
        """
        Truncate a given HTML string to a specified number of characters.
        
        Args:
        html_string (str): The HTML string to be truncated.
        num_chars (int): The number of characters to which the string should be truncated.
        
        Returns:
        str: The truncated HTML string.
        
        Example:
        >>> truncatechars_html('<p>one <a href="#">two - three <br>four</a> five</p>', 4)
        '<p>one…</p>'
        """

        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 4
            ),
            "<p>one…</p>",
        )

    def test_truncate2(self):
        """
        Truncate a given HTML string to a specified number of characters while preserving the HTML structure.
        
        Args:
        html_string (str): The HTML string to be truncated.
        num_chars (int): The maximum number of characters to include in the truncated string.
        
        Returns:
        str: The truncated HTML string with the specified number of characters, preserving the HTML structure.
        
        Example:
        >>> truncatechars_html('<p>one <a href="#">two - three <br>four</a> five</p
        """

        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 9
            ),
            '<p>one <a href="#">two …</a></p>',
        )

    def test_truncate3(self):
        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 100
            ),
            '<p>one <a href="#">two - three <br>four</a> five</p>',
        )

    def test_truncate_unicode(self):
        self.assertEqual(
            truncatechars_html("<b>\xc5ngstr\xf6m</b> was here", 3), "<b>\xc5n…</b>"
        )

    def test_truncate_something(self):
        self.assertEqual(truncatechars_html("a<b>b</b>c", 3), "a<b>b</b>c")

    def test_invalid_arg(self):
        html = '<p>one <a href="#">two - three <br>four</a> five</p>'
        self.assertEqual(truncatechars_html(html, "a"), html)
