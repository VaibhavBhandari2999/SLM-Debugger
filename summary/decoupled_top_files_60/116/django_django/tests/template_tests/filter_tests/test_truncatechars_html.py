from django.template.defaultfilters import truncatechars_html
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_truncate_zero(self):
        """
        Truncate a given HTML string to a specified number of characters, with special handling for zero characters.
        
        Parameters:
        html_str (str): The HTML string to be truncated.
        num_chars (int): The number of characters to truncate to. If zero, the function returns an ellipsis ("…").
        
        Returns:
        str: The truncated HTML string, or an ellipsis if the specified number of characters is zero.
        
        Example:
        >>> truncatechars_html('<p>one <a href="#">two
        """

        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 0
            ),
            "…",
        )

    def test_truncate(self):
        self.assertEqual(
            truncatechars_html(
                '<p>one <a href="#">two - three <br>four</a> five</p>', 4
            ),
            "<p>one…</p>",
        )

    def test_truncate2(self):
        """
        Truncate a string containing HTML to a specified number of characters, ensuring that the truncation does not break HTML tags. The function takes a string `html_content` and an integer `max_length` as input. It returns a truncated version of the string, ensuring that the truncation does not cut through HTML tags. If the input string is shorter than `max_length`, it is returned unchanged. If truncation is necessary, the function will truncate the content while preserving the integrity of the HTML structure
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
