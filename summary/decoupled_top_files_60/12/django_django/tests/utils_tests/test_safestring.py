from django.template import Context, Template
from django.test import SimpleTestCase
from django.utils import html
from django.utils.functional import lazy, lazystr
from django.utils.safestring import SafeData, mark_safe


class customescape(str):
    def __html__(self):
        """
        The `__html__` method returns a string representation of the object, with specific characters replaced to simulate HTML escaping. This method is used to ensure that the output can be safely included in HTML content without causing parsing issues.
        
        Parameters:
        None
        
        Returns:
        str: A string representation of the object with '<' replaced by '<<' and '>' replaced by '>>'.
        
        Note:
        This method is a simplified and intentionally incorrect implementation of HTML escaping for demonstration purposes. In a real-world scenario
        """

        # implement specific and obviously wrong escaping
        # in order to be able to tell for sure when it runs
        return self.replace('<', '<<').replace('>', '>>')


class SafeStringTest(SimpleTestCase):
    def assertRenderEqual(self, tpl, expected, **context):
        context = Context(context)
        tpl = Template(tpl)
        self.assertEqual(tpl.render(context), expected)

    def test_mark_safe(self):
        """
        Tests the behavior of the `mark_safe` function.
        
        This function tests the `mark_safe` function by creating a marked safe string 'a&b' and then rendering it in two different ways. The first rendering is without any additional escaping, which should output the original string 'a&b'. The second rendering uses the `force_escape` filter, which should escape the ampersand, resulting in 'a&amp;b'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        -
        """

        s = mark_safe('a&b')

        self.assertRenderEqual('{{ s }}', 'a&b', s=s)
        self.assertRenderEqual('{{ s|force_escape }}', 'a&amp;b', s=s)

    def test_mark_safe_str(self):
        """
        Calling str() on a SafeString instance doesn't lose the safe status.
        """
        s = mark_safe('a&b')
        self.assertIsInstance(str(s), type(s))

    def test_mark_safe_object_implementing_dunder_html(self):
        e = customescape('<a&b>')
        s = mark_safe(e)
        self.assertIs(s, e)

        self.assertRenderEqual('{{ s }}', '<<a&b>>', s=s)
        self.assertRenderEqual('{{ s|force_escape }}', '&lt;a&amp;b&gt;', s=s)

    def test_mark_safe_lazy(self):
        s = lazystr('a&b')

        self.assertIsInstance(mark_safe(s), SafeData)
        self.assertRenderEqual('{{ s }}', 'a&b', s=mark_safe(s))

    def test_mark_safe_object_implementing_dunder_str(self):
        """
        Tests that a Django `mark_safe` function correctly handles an object implementing the `__str__` method. The function creates an instance of a custom object `Obj` which returns '<obj>' when `__str__` is called. The `mark_safe` function is then used to mark this object as safe for HTML rendering. The test asserts that when the object is rendered in a template context, it outputs '<obj>'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        """

        class Obj:
            def __str__(self):
                return '<obj>'

        s = mark_safe(Obj())

        self.assertRenderEqual('{{ s }}', '<obj>', s=s)

    def test_mark_safe_result_implements_dunder_html(self):
        self.assertEqual(mark_safe('a&b').__html__(), 'a&b')

    def test_mark_safe_lazy_result_implements_dunder_html(self):
        self.assertEqual(mark_safe(lazystr('a&b')).__html__(), 'a&b')

    def test_add_lazy_safe_text_and_safe_text(self):
        s = html.escape(lazystr('a'))
        s += mark_safe('&b')
        self.assertRenderEqual('{{ s }}', 'a&b', s=s)

        s = html.escapejs(lazystr('a'))
        s += mark_safe('&b')
        self.assertRenderEqual('{{ s }}', 'a&b', s=s)

    def test_mark_safe_as_decorator(self):
        """
        mark_safe used as a decorator leaves the result of a function
        unchanged.
        """
        def clean_string_provider():
            return '<html><body>dummy</body></html>'

        self.assertEqual(mark_safe(clean_string_provider)(), clean_string_provider())

    def test_mark_safe_decorator_does_not_affect_dunder_html(self):
        """
        mark_safe doesn't affect a callable that has an __html__() method.
        """
        class SafeStringContainer:
            def __html__(self):
                return '<html></html>'

        self.assertIs(mark_safe(SafeStringContainer), SafeStringContainer)

    def test_mark_safe_decorator_does_not_affect_promises(self):
        """
        mark_safe doesn't affect lazy strings (Promise objects).
        """
        def html_str():
            return '<html></html>'

        lazy_str = lazy(html_str, str)()
        self.assertEqual(mark_safe(lazy_str), html_str())
al(mark_safe(lazy_str), html_str())
