from django.template.defaultfilters import unordered_list
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ..utils import setup


class UnorderedListTests(SimpleTestCase):
    @setup({"unordered_list01": "{{ a|unordered_list }}"})
    def test_unordered_list01(self):
        output = self.engine.render_to_string("unordered_list01", {"a": ["x>", ["<y"]]})
        self.assertEqual(
            output, "\t<li>x&gt;\n\t<ul>\n\t\t<li>&lt;y</li>\n\t</ul>\n\t</li>"
        )

    @setup(
        {
            "unordered_list02": (
                "{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}"
            )
        }
    )
    def test_unordered_list02(self):
        output = self.engine.render_to_string("unordered_list02", {"a": ["x>", ["<y"]]})
        self.assertEqual(output, "\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>")

    @setup({"unordered_list03": "{{ a|unordered_list }}"})
    def test_unordered_list03(self):
        """
        Tests the rendering of an unordered list with a nested unordered list and a marked safe string.
        
        Parameters:
        - self: The instance of the test case class.
        
        Returns:
        - None: This function asserts the expected output against the actual output.
        
        Key Parameters:
        - a (list): A list containing an element 'x>' and a nested list ['<y'] marked as safe.
        
        Expected Output:
        - A string representing the HTML unordered list structure, with 'x>' as a list item and '<y
        """

        output = self.engine.render_to_string(
            "unordered_list03", {"a": ["x>", [mark_safe("<y")]]}
        )
        self.assertEqual(
            output, "\t<li>x&gt;\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>"
        )

    @setup(
        {
            "unordered_list04": (
                "{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}"
            )
        }
    )
    def test_unordered_list04(self):
        output = self.engine.render_to_string(
            "unordered_list04", {"a": ["x>", [mark_safe("<y")]]}
        )
        self.assertEqual(output, "\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>")

    @setup(
        {
            "unordered_list05": (
                "{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}"
            )
        }
    )
    def test_unordered_list05(self):
        output = self.engine.render_to_string("unordered_list05", {"a": ["x>", ["<y"]]})
        self.assertEqual(output, "\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>")


class FunctionTests(SimpleTestCase):
    def test_list(self):
        """
        Tests the unordered_list function.
        
        Args:
        self: The instance of the test class.
        
        This function checks if the unordered_list function correctly generates an HTML unordered list from a list of items. The function takes a list of strings as input and returns a string representing the HTML unordered list. The test asserts that the output matches the expected HTML structure for the given list of items.
        """

        self.assertEqual(
            unordered_list(["item 1", "item 2"]), "\t<li>item 1</li>\n\t<li>item 2</li>"
        )

    def test_list_gettext(self):
        """
        Tests the unordered_list function with a list containing both regular strings and gettext_lazy objects.
        
        Parameters:
        - self: The current test case instance.
        
        Returns:
        - None: This function asserts the output of the unordered_list function, so it does not return any value.
        
        Key elements:
        - The function uses the `gettext_lazy` object to handle localization.
        - The input to the `unordered_list` function is a list containing a regular string and a `gettext_lazy` object.
        - The expected output is an
        """

        self.assertEqual(
            unordered_list(["item 1", gettext_lazy("item 2")]),
            "\t<li>item 1</li>\n\t<li>item 2</li>",
        )

    def test_nested(self):
        self.assertEqual(
            unordered_list(["item 1", ["item 1.1"]]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</ul>\n\t</li>",
        )

    def test_nested2(self):
        self.assertEqual(
            unordered_list(["item 1", ["item 1.1", "item1.2"], "item 2"]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t\t<li>item1.2"
            "</li>\n\t</ul>\n\t</li>\n\t<li>item 2</li>",
        )

    def test_nested3(self):
        self.assertEqual(
            unordered_list(["item 1", "item 2", ["item 2.1"]]),
            "\t<li>item 1</li>\n\t<li>item 2\n\t<ul>\n\t\t<li>item 2.1"
            "</li>\n\t</ul>\n\t</li>",
        )

    def test_nested_multiple(self):
        self.assertEqual(
            unordered_list(["item 1", ["item 1.1", ["item 1.1.1", ["item 1.1.1.1"]]]]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1\n\t\t<ul>\n\t\t\t<li>"
            "item 1.1.1\n\t\t\t<ul>\n\t\t\t\t<li>item 1.1.1.1</li>\n\t\t\t"
            "</ul>\n\t\t\t</li>\n\t\t</ul>\n\t\t</li>\n\t</ul>\n\t</li>",
        )

    def test_nested_multiple2(self):
        self.assertEqual(
            unordered_list(["States", ["Kansas", ["Lawrence", "Topeka"], "Illinois"]]),
            "\t<li>States\n\t<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>"
            "Lawrence</li>\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>"
            "\n\t\t<li>Illinois</li>\n\t</ul>\n\t</li>",
        )

    def test_autoescape(self):
        """
        Test the autoescaping behavior of the unordered_list function.
        This function checks if the unordered_list function correctly escapes HTML content within the list items. The function takes a single parameter, a list of strings, where some strings may contain HTML tags. The function returns a string representing an unordered list with the provided items, ensuring that any HTML tags are properly escaped to prevent XSS attacks.
        
        Parameters:
        - items (list): A list of strings, where some strings may contain HTML tags.
        
        Returns:
        - str:
        """

        self.assertEqual(
            unordered_list(["<a>item 1</a>", "item 2"]),
            "\t<li>&lt;a&gt;item 1&lt;/a&gt;</li>\n\t<li>item 2</li>",
        )

    def test_autoescape_off(self):
        self.assertEqual(
            unordered_list(["<a>item 1</a>", "item 2"], autoescape=False),
            "\t<li><a>item 1</a></li>\n\t<li>item 2</li>",
        )

    def test_ulitem(self):
        class ULItem:
            def __init__(self, title):
                self.title = title

            def __str__(self):
                return "ulitem-%s" % str(self.title)

        a = ULItem("a")
        b = ULItem("b")
        c = ULItem("<a>c</a>")
        self.assertEqual(
            unordered_list([a, b, c]),
            "\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t"
            "<li>ulitem-&lt;a&gt;c&lt;/a&gt;</li>",
        )

        def item_generator():
            yield from (a, b, c)

        self.assertEqual(
            unordered_list(item_generator()),
            "\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t"
            "<li>ulitem-&lt;a&gt;c&lt;/a&gt;</li>",
        )

    def test_nested_generators(self):
        """
        Tests the behavior of nested generators.
        
        This function checks the correct handling of nested generators. The `item_generator` yields a sequence of items, including a nested generator. The `inner_generator` yields the items 'B' and 'C'. The `item_generator` yields 'A', the `inner_generator`, and 'D'. The test verifies that the output is correctly formatted as an unordered list.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - `item_generator`: Y
        """

        def inner_generator():
            yield from ("B", "C")

        def item_generator():
            yield "A"
            yield inner_generator()
            yield "D"

        self.assertEqual(
            unordered_list(item_generator()),
            "\t<li>A\n\t<ul>\n\t\t<li>B</li>\n\t\t<li>C</li>\n\t</ul>\n\t</li>\n\t"
            "<li>D</li>",
        )

    def test_ulitem_autoescape_off(self):
        class ULItem:
            def __init__(self, title):
                self.title = title

            def __str__(self):
                return "ulitem-%s" % str(self.title)

        a = ULItem("a")
        b = ULItem("b")
        c = ULItem("<a>c</a>")
        self.assertEqual(
            unordered_list([a, b, c], autoescape=False),
            "\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-<a>c</a></li>",
        )

        def item_generator():
            yield from (a, b, c)

        self.assertEqual(
            unordered_list(item_generator(), autoescape=False),
            "\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-<a>c</a></li>",
        )
