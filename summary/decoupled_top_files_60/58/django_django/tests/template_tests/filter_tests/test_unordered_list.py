from django.template.defaultfilters import unordered_list
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ..utils import setup


class UnorderedListTests(SimpleTestCase):

    @setup({'unordered_list01': '{{ a|unordered_list }}'})
    def test_unordered_list01(self):
        output = self.engine.render_to_string('unordered_list01', {'a': ['x>', ['<y']]})
        self.assertEqual(output, '\t<li>x&gt;\n\t<ul>\n\t\t<li>&lt;y</li>\n\t</ul>\n\t</li>')

    @setup({'unordered_list02': '{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}'})
    def test_unordered_list02(self):
        output = self.engine.render_to_string('unordered_list02', {'a': ['x>', ['<y']]})
        self.assertEqual(output, '\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>')

    @setup({'unordered_list03': '{{ a|unordered_list }}'})
    def test_unordered_list03(self):
        output = self.engine.render_to_string('unordered_list03', {'a': ['x>', [mark_safe('<y')]]})
        self.assertEqual(output, '\t<li>x&gt;\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>')

    @setup({'unordered_list04': '{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}'})
    def test_unordered_list04(self):
        output = self.engine.render_to_string('unordered_list04', {'a': ['x>', [mark_safe('<y')]]})
        self.assertEqual(output, '\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>')

    @setup({'unordered_list05': '{% autoescape off %}{{ a|unordered_list }}{% endautoescape %}'})
    def test_unordered_list05(self):
        output = self.engine.render_to_string('unordered_list05', {'a': ['x>', ['<y']]})
        self.assertEqual(output, '\t<li>x>\n\t<ul>\n\t\t<li><y</li>\n\t</ul>\n\t</li>')


class FunctionTests(SimpleTestCase):

    def test_list(self):
        self.assertEqual(unordered_list(['item 1', 'item 2']), '\t<li>item 1</li>\n\t<li>item 2</li>')

    def test_list_gettext(self):
        """
        Test the unordered_list function with a list containing both regular strings and gettext_lazy objects.
        
        Parameters:
        - items (list): A list of strings and gettext_lazy objects.
        
        Returns:
        - str: An HTML unordered list string with the items as list items.
        
        Example:
        >>> test_list_gettext(['item 1', gettext_lazy('item 2')])
        '\t<li>item 1</li>\n\t<li>item 2</li>'
        """

        self.assertEqual(
            unordered_list(['item 1', gettext_lazy('item 2')]),
            '\t<li>item 1</li>\n\t<li>item 2</li>'
        )

    def test_nested(self):
        self.assertEqual(
            unordered_list(['item 1', ['item 1.1']]),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</ul>\n\t</li>',
        )

    def test_nested2(self):
        self.assertEqual(
            unordered_list(['item 1', ['item 1.1', 'item1.2'], 'item 2']),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t\t<li>item1.2'
            '</li>\n\t</ul>\n\t</li>\n\t<li>item 2</li>',
        )

    def test_nested3(self):
        self.assertEqual(
            unordered_list(['item 1', 'item 2', ['item 2.1']]),
            '\t<li>item 1</li>\n\t<li>item 2\n\t<ul>\n\t\t<li>item 2.1'
            '</li>\n\t</ul>\n\t</li>',
        )

    def test_nested_multiple(self):
        """
        Test nested multiple items in an unordered list.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the generated HTML does not match the expected output.
        
        This function tests the generation of an unordered list with nested items. The input is a list containing multiple items, some of which are themselves lists representing nested items. The expected output is a string representing the HTML code for the nested unordered list, with appropriate indentation to reflect the nesting structure.
        """

        self.assertEqual(
            unordered_list(['item 1', ['item 1.1', ['item 1.1.1', ['item 1.1.1.1']]]]),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1\n\t\t<ul>\n\t\t\t<li>'
            'item 1.1.1\n\t\t\t<ul>\n\t\t\t\t<li>item 1.1.1.1</li>\n\t\t\t'
            '</ul>\n\t\t\t</li>\n\t\t</ul>\n\t\t</li>\n\t</ul>\n\t</li>',
        )

    def test_nested_multiple2(self):
        self.assertEqual(
            unordered_list(['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]),
            '\t<li>States\n\t<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>'
            'Lawrence</li>\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>'
            '\n\t\t<li>Illinois</li>\n\t</ul>\n\t</li>',
        )

    def test_autoescape(self):
        """
        Test the autoescaping behavior of the unordered_list function.
        This function checks if the unordered_list function correctly autoescapes HTML content within the list items. It takes a single parameter, a list of strings, where some strings may contain HTML tags. The function returns a string representing an unordered list with the provided items, ensuring that any HTML tags are properly escaped to prevent XSS attacks.
        
        Parameters:
        - items (list): A list of strings, where some strings may contain HTML tags.
        
        Returns:
        - str
        """

        self.assertEqual(
            unordered_list(['<a>item 1</a>', 'item 2']),
            '\t<li>&lt;a&gt;item 1&lt;/a&gt;</li>\n\t<li>item 2</li>',
        )

    def test_autoescape_off(self):
        """
        Test the unordered_list function with autoescape disabled.
        
        This test checks that the unordered_list function correctly renders a list
        without escaping HTML content when autoescape is set to False. The function
        takes a list of items and an autoescape flag as input and returns a string
        representing the HTML unordered list.
        
        Parameters:
        - items (list): A list of strings containing the items to be included in the
        unordered list.
        - autoescape (bool): A flag indicating whether HTML content should be
        """

        self.assertEqual(
            unordered_list(['<a>item 1</a>', 'item 2'], autoescape=False),
            '\t<li><a>item 1</a></li>\n\t<li>item 2</li>',
        )

    def test_ulitem(self):
        class ULItem:
            def __init__(self, title):
                self.title = title

            def __str__(self):
                return 'ulitem-%s' % str(self.title)

        a = ULItem('a')
        b = ULItem('b')
        c = ULItem('<a>c</a>')
        self.assertEqual(
            unordered_list([a, b, c]),
            '\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-&lt;a&gt;c&lt;/a&gt;</li>',
        )

        def item_generator():
            yield from (a, b, c)

        self.assertEqual(
            unordered_list(item_generator()),
            '\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-&lt;a&gt;c&lt;/a&gt;</li>',
        )

    def test_nested_generators(self):
        def inner_generator():
            yield from ('B', 'C')

        def item_generator():
            yield 'A'
            yield inner_generator()
            yield 'D'

        self.assertEqual(
            unordered_list(item_generator()),
            '\t<li>A\n\t<ul>\n\t\t<li>B</li>\n\t\t<li>C</li>\n\t</ul>\n\t</li>\n\t<li>D</li>',
        )

    def test_ulitem_autoescape_off(self):
        """
        Test the unordered_list function with autoescape disabled.
        
        This test checks the behavior of the unordered_list function when autoescape is set to False. It uses a custom ULItem class to generate list items. The function is tested with both a list and a generator as input.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - autoescape (bool): Set to False to disable autoescaping.
        
        Test Cases:
        - A list of ULItem instances is provided, including one with a
        """

        class ULItem:
            def __init__(self, title):
                self.title = title

            def __str__(self):
                return 'ulitem-%s' % str(self.title)

        a = ULItem('a')
        b = ULItem('b')
        c = ULItem('<a>c</a>')
        self.assertEqual(
            unordered_list([a, b, c], autoescape=False),
            '\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-<a>c</a></li>',
        )

        def item_generator():
            yield from (a, b, c)

        self.assertEqual(
            unordered_list(item_generator(), autoescape=False),
            '\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>\n\t<li>ulitem-<a>c</a></li>',
        )
