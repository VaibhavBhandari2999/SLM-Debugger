from django.template.defaultfilters import join
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class JoinTests(SimpleTestCase):

    @setup({'join01': '{{ a|join:", " }}'})
    def test_join01(self):
        output = self.engine.render_to_string('join01', {'a': ['alpha', 'beta & me']})
        self.assertEqual(output, 'alpha, beta &amp; me')

    @setup({'join02': '{% autoescape off %}{{ a|join:", " }}{% endautoescape %}'})
    def test_join02(self):
        output = self.engine.render_to_string('join02', {'a': ['alpha', 'beta & me']})
        self.assertEqual(output, 'alpha, beta & me')

    @setup({'join03': '{{ a|join:" &amp; " }}'})
    def test_join03(self):
        output = self.engine.render_to_string('join03', {'a': ['alpha', 'beta & me']})
        self.assertEqual(output, 'alpha &amp; beta &amp; me')

    @setup({'join04': '{% autoescape off %}{{ a|join:" &amp; " }}{% endautoescape %}'})
    def test_join04(self):
        output = self.engine.render_to_string('join04', {'a': ['alpha', 'beta & me']})
        self.assertEqual(output, 'alpha &amp; beta & me')

    # Joining with unsafe joiners doesn't result in unsafe strings.
    @setup({'join05': '{{ a|join:var }}'})
    def test_join05(self):
        output = self.engine.render_to_string('join05', {'a': ['alpha', 'beta & me'], 'var': ' & '})
        self.assertEqual(output, 'alpha &amp; beta &amp; me')

    @setup({'join06': '{{ a|join:var }}'})
    def test_join06(self):
        output = self.engine.render_to_string('join06', {'a': ['alpha', 'beta & me'], 'var': mark_safe(' & ')})
        self.assertEqual(output, 'alpha & beta &amp; me')

    @setup({'join07': '{{ a|join:var|lower }}'})
    def test_join07(self):
        output = self.engine.render_to_string('join07', {'a': ['Alpha', 'Beta & me'], 'var': ' & '})
        self.assertEqual(output, 'alpha &amp; beta &amp; me')

    @setup({'join08': '{{ a|join:var|lower }}'})
    def test_join08(self):
        output = self.engine.render_to_string('join08', {'a': ['Alpha', 'Beta & me'], 'var': mark_safe(' & ')})
        self.assertEqual(output, 'alpha & beta &amp; me')


class FunctionTests(SimpleTestCase):

    def test_list(self):
        self.assertEqual(join([0, 1, 2], 'glue'), '0glue1glue2')

    def test_autoescape(self):
        """
        Tests the autoescaping functionality of the join function.
        
        This function checks if the join function correctly autoescapes HTML tags and ensures that the output is properly formatted with HTML entities. The function takes a list of strings and a separator, and returns a single string with the elements joined by the separator. The key parameters are:
        - `parts`: A list of strings to be joined.
        - `separator`: A string used to separate the elements in the output.
        
        The function asserts that the output is the same
        """

        self.assertEqual(
            join(['<a>', '<img>', '</a>'], '<br>'),
            '&lt;a&gt;&lt;br&gt;&lt;img&gt;&lt;br&gt;&lt;/a&gt;',
        )

    def test_autoescape_off(self):
        """
        Test the behavior of the `join` function when `autoescape` is set to `False`.
        
        Parameters:
        - parts (list): A list of strings to be joined together.
        - separator (str): The separator to use between each part. Default is '<br>'.
        - autoescape (bool): Whether to auto-escape special characters. Default is False.
        
        Returns:
        - str: The joined string with parts separated by the specified separator and without auto-escaping special characters.
        """

        self.assertEqual(
            join(['<a>', '<img>', '</a>'], '<br>', autoescape=False),
            '<a>&lt;br&gt;<img>&lt;br&gt;</a>',
        )

    def test_noniterable_arg(self):
        obj = object()
        self.assertEqual(join(obj, '<br>'), obj)

    def test_noniterable_arg_autoescape_off(self):
        obj = object()
        self.assertEqual(join(obj, '<br>', autoescape=False), obj)
