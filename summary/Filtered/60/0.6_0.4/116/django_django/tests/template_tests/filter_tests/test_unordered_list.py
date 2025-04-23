from django.template.defaultfilters import unordered_list
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ..utils import setup


class UnorderedListTests(SimpleTestCase):
    @setup({"unordered_list01": "{{ a|unordered_list }}"})
    def test_unordered_list01(self):
        """
        Test rendering an unordered list with nested elements.
        
        This function tests the rendering of an unordered list where the first item is a string with a '>' character, and the second item is a list containing a single string with a '<' character. The expected output is an HTML unordered list with the appropriate escaping of special characters.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> test_unordered_list01()
        # The function will render the following HTML:
        # <ul>
        """

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
        Tests the rendering of an unordered list with a nested list item containing a marked safe HTML string.
        
        Args:
        self: The test case instance.
        
        Returns:
        None. This function asserts the rendered output against an expected string.
        
        Key Parameters:
        - a (list): A list containing an item and a nested list item with a marked safe HTML string.
        
        Expected Output:
        A string representing the HTML output of the unordered list, which includes the outer list item, an unordered nested list, and a
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
        self.assertEqual(
            unordered_list(["item 1", "item 2"]), "\t<li>item 1</li>\n\t<li>item 2</li>"
        )

    def test_list_gettext(self):
        self.assertEqual(
            unordered_list(["item 1", gettext_lazy("item 2")]),
            "\t<li>item 1</li>\n\t<li>item 2</li>",
        )

    def test_nested(self):
        """
        Tests the unordered list function with a nested item.
        This function checks if the unordered_list function correctly formats an unordered list with a nested item.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> test_nested()
        Asserts that the unordered_list function returns the correct HTML for an unordered list with a nested item.
        The expected output is:
        \t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</
        """

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
        """
        Tests the unordered_list function with nested lists.
        This function checks the unordered_list function's ability to handle nested lists, specifically a top-level list containing a string and a nested list with two strings. The expected output is a string representing an HTML unordered list with appropriate indentation for nested elements.
        
        Parameters:
        - None (the test is self-contained within the test method)
        
        Returns:
        - None (the test asserts the expected output against the actual output)
        
        Key Elements:
        - unordered_list: The function being tested
        """

        self.assertEqual(
            unordered_list(["States", ["Kansas", ["Lawrence", "Topeka"], "Illinois"]]),
            "\t<li>States\n\t<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>"
            "Lawrence</li>\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>"
            "\n\t\t<li>Illinois</li>\n\t</ul>\n\t</li>",
        )

    def test_autoescape(self):
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
