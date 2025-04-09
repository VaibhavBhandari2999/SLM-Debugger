from django.template.defaultfilters import unordered_list
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ..utils import setup


class UnorderedListTests(SimpleTestCase):
    @setup({"unordered_list01": "{{ a|unordered_list }}"})
    def test_unordered_list01(self):
        """
        Tests rendering of an unordered list with nested elements.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the rendered output does not match the expected result.
        
        Important Functions:
        - `render_to_string`: Renders the template with the given context.
        - `assertEqual`: Compares the rendered output with the expected result.
        
        Input Variables:
        - `a`: A list containing a string and another list.
        
        Output Variables:
        - `output
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
        Tests rendering of an unordered list with nested elements using the engine's render_to_string method. The input is a dictionary containing a list with a string and a nested list, and the output is a formatted HTML string representing the rendered list.
        
        Args:
        None (The test is run internally within the class)
        
        Returns:
        None (The test asserts the expected output against the actual output)
        
        Important Functions:
        - `render_to_string`: Renders the template with the given context.
        -
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
        """
        Tests rendering of an unordered list with nested elements using the engine's render_to_string method. The input is a dictionary containing a key 'a' with a value that is a list containing a string and another list with a mark_safe element. The expected output is a string representing the HTML unordered list structure with the nested elements properly formatted.
        """

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
        Test the unordered_list function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the unordered_list function, which takes a list of items and returns an HTML unordered list string. The input is a list of strings, and the output is a string containing the HTML representation of the unordered list with each item wrapped in <li> tags.
        """

        self.assertEqual(
            unordered_list(["item 1", "item 2"]), "\t<li>item 1</li>\n\t<li>item 2</li>"
        )

    def test_list_gettext(self):
        """
        Tests the `unordered_list` function, which takes a list of items and returns an HTML unordered list string. The function uses `gettext_lazy` to handle localization of one of the items in the list.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        None
        
        Example:
        >>> test_list_gettext()
        \t<li>item 1</li>\n\t<li>item 2</li>
        """

        self.assertEqual(
            unordered_list(["item 1", gettext_lazy("item 2")]),
            "\t<li>item 1</li>\n\t<li>item 2</li>",
        )

    def test_nested(self):
        """
        Test the `unordered_list` function with nested items.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output of `unordered_list` does not match the expected result.
        
        Important Functions:
        - `unordered_list`: Generates an unordered list from a given list of items, including nested lists.
        """

        self.assertEqual(
            unordered_list(["item 1", ["item 1.1"]]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</ul>\n\t</li>",
        )

    def test_nested2(self):
        """
        Test nested unordered list generation.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the generated HTML does not match the expected output.
        
        Summary:
        This function tests the generation of a nested unordered list from a given list of items. It uses the `unordered_list` function to convert the input list into an HTML unordered list with appropriate indentation for nested items. The test checks if the generated HTML matches the expected output, which includes proper nesting and indentation of
        """

        self.assertEqual(
            unordered_list(["item 1", ["item 1.1", "item1.2"], "item 2"]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t\t<li>item1.2"
            "</li>\n\t</ul>\n\t</li>\n\t<li>item 2</li>",
        )

    def test_nested3(self):
        """
        Test the `unordered_list` function with nested items.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output of `unordered_list` does not match the expected result.
        
        Important Functions:
        - `unordered_list`: Generates an HTML unordered list from a given list of items, including nested lists.
        
        Input:
        - A list containing strings and sublists representing nested items.
        
        Output:
        - A string representing the HTML unordered list with nested
        """

        self.assertEqual(
            unordered_list(["item 1", "item 2", ["item 2.1"]]),
            "\t<li>item 1</li>\n\t<li>item 2\n\t<ul>\n\t\t<li>item 2.1"
            "</li>\n\t</ul>\n\t</li>",
        )

    def test_nested_multiple(self):
        """
        Tests the `unordered_list` function with nested items.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `unordered_list` function by comparing its output against an expected string representation of a nested unordered list. The input is a list containing multiple levels of nested items, and the output is a formatted string representing the nested list structure.
        """

        self.assertEqual(
            unordered_list(["item 1", ["item 1.1", ["item 1.1.1", ["item 1.1.1.1"]]]]),
            "\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1\n\t\t<ul>\n\t\t\t<li>"
            "item 1.1.1\n\t\t\t<ul>\n\t\t\t\t<li>item 1.1.1.1</li>\n\t\t\t"
            "</ul>\n\t\t\t</li>\n\t\t</ul>\n\t\t</li>\n\t</ul>\n\t</li>",
        )

    def test_nested_multiple2(self):
        """
        Tests the `unordered_list` function with nested lists, verifying that it correctly formats a list with multiple levels of nesting into an HTML unordered list (ul) structure.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `unordered_list`: The function being tested, which takes a nested list and converts it into an HTML unordered list string.
        
        Input:
        - A nested list containing strings representing items at different levels of nesting.
        
        Output:
        - A string
        """

        self.assertEqual(
            unordered_list(["States", ["Kansas", ["Lawrence", "Topeka"], "Illinois"]]),
            "\t<li>States\n\t<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>"
            "Lawrence</li>\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>"
            "\n\t\t<li>Illinois</li>\n\t</ul>\n\t</li>",
        )

    def test_autoescape(self):
        """
        Test the autoescaping behavior of the `unordered_list` function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the autoescaping behavior of the `unordered_list` function, which takes a list of items and returns an HTML unordered list with each item properly escaped. The test checks if the function correctly escapes HTML tags within the items.
        
        Important Functions:
        - `unordered_list`: The function being tested, which generates an HTML unordered list from a list
        """

        self.assertEqual(
            unordered_list(["<a>item 1</a>", "item 2"]),
            "\t<li>&lt;a&gt;item 1&lt;/a&gt;</li>\n\t<li>item 2</li>",
        )

    def test_autoescape_off(self):
        """
        Tests the `unordered_list` function with `autoescape` set to `False`. The function takes a list of items, where each item can be a string or a tuple containing a string and an `autoescape` flag. When `autoescape` is set to `False`, the function returns a string with the items formatted as HTML `<li>` tags without escaping the content. The expected output is a string containing two `<li>` tags, one for each item in the input list.
        """

        self.assertEqual(
            unordered_list(["<a>item 1</a>", "item 2"], autoescape=False),
            "\t<li><a>item 1</a></li>\n\t<li>item 2</li>",
        )

    def test_ulitem(self):
        """
        Generates an unordered list from a collection of ULItem objects or an iterable.
        
        Args:
        items (iterable): An iterable containing ULItem objects or a generator.
        
        Returns:
        str: The HTML representation of the unordered list.
        
        Examples:
        >>> a = ULItem("a")
        >>> b = ULItem("b")
        >>> c = ULItem("<a>c</a>")
        >>> unordered_list([a, b, c])
        '\t<li>ulitem
        """

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
            """
            Generates items using an inner generator.
            
            Yields:
            str: Items generated by the function, including "A" and the result of the inner_generator().
            """

            yield from (a, b, c)

        self.assertEqual(
            unordered_list(item_generator()),
            "\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t"
            "<li>ulitem-&lt;a&gt;c&lt;/a&gt;</li>",
        )

    def test_nested_generators(self):
        """
        Tests the behavior of nested generators.
        
        This test checks how the `item_generator` function processes and yields items, including nested generators. The `inner_generator` function is used to generate a sequence of items 'B' and 'C', which are then included within the output generated by `item_generator`. The `unordered_list` function is expected to format these items into an unordered list structure, with 'A' and 'D' being top-level items, and 'B' and 'C'
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
        """
        Test the `unordered_list` function with `autoescape` set to False.
        
        This test checks that the `unordered_list` function correctly renders
        items from an iterable or list without escaping HTML content. It uses
        the `ULItem` class to create items with different types of titles,
        including plain text and HTML tags. The test ensures that the generated
        HTML is as expected when using both a list and a generator.
        
        Args:
        None
        
        Returns:
        """

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
