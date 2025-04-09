from django.template.defaultfilters import join
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class JoinTests(SimpleTestCase):
    @setup({"join01": '{{ a|join:", " }}'})
    def test_join01(self):
        output = self.engine.render_to_string("join01", {"a": ["alpha", "beta & me"]})
        self.assertEqual(output, "alpha, beta &amp; me")

    @setup({"join02": '{% autoescape off %}{{ a|join:", " }}{% endautoescape %}'})
    def test_join02(self):
        output = self.engine.render_to_string("join02", {"a": ["alpha", "beta & me"]})
        self.assertEqual(output, "alpha, beta & me")

    @setup({"join03": '{{ a|join:" &amp; " }}'})
    def test_join03(self):
        output = self.engine.render_to_string("join03", {"a": ["alpha", "beta & me"]})
        self.assertEqual(output, "alpha &amp; beta &amp; me")

    @setup({"join04": '{% autoescape off %}{{ a|join:" &amp; " }}{% endautoescape %}'})
    def test_join04(self):
        output = self.engine.render_to_string("join04", {"a": ["alpha", "beta & me"]})
        self.assertEqual(output, "alpha &amp; beta & me")

    # Joining with unsafe joiners doesn't result in unsafe strings.
    @setup({"join05": "{{ a|join:var }}"})
    def test_join05(self):
        """
        Tests rendering of template with join filter using custom separator.
        
        Args:
        engine (Engine): The template engine instance.
        
        Inputs:
        - a: A list containing string elements.
        - var: Custom separator string.
        
        Outputs:
        - Rendered string with joined list elements separated by the custom separator.
        """

        output = self.engine.render_to_string(
            "join05", {"a": ["alpha", "beta & me"], "var": " & "}
        )
        self.assertEqual(output, "alpha &amp; beta &amp; me")

    @setup({"join06": "{{ a|join:var }}"})
    def test_join06(self):
        """
        Tests rendering of template with join filter using a list and a marked safe string.
        The join filter concatenates list elements with the specified separator, which is a marked safe string containing an ampersand.
        The expected output is 'alpha & beta &amp; me', where 'beta & me' is properly escaped.
        """

        output = self.engine.render_to_string(
            "join06", {"a": ["alpha", "beta & me"], "var": mark_safe(" & ")}
        )
        self.assertEqual(output, "alpha & beta &amp; me")

    @setup({"join07": "{{ a|join:var|lower }}"})
    def test_join07(self):
        """
        Tests rendering of template with join filter using custom separator.
        
        Args:
        engine (Engine): The template engine instance.
        
        Inputs:
        - a: A list containing string elements.
        - var: Custom separator string.
        
        Outputs:
        - Rendered string with joined list elements separated by the custom separator.
        """

        output = self.engine.render_to_string(
            "join07", {"a": ["Alpha", "Beta & me"], "var": " & "}
        )
        self.assertEqual(output, "alpha &amp; beta &amp; me")

    @setup({"join08": "{{ a|join:var|lower }}"})
    def test_join08(self):
        """
        Tests rendering of template with join filter using a list and a marked safe string.
        The join filter concatenates list elements with the specified separator (' & ') and escapes special characters in the output.
        Input: Dictionary containing a list and a marked safe string.
        Output: Rendered string with joined list elements separated by ' & ' and special characters escaped.
        """

        output = self.engine.render_to_string(
            "join08", {"a": ["Alpha", "Beta & me"], "var": mark_safe(" & ")}
        )
        self.assertEqual(output, "alpha & beta &amp; me")


class FunctionTests(SimpleTestCase):
    def test_list(self):
        self.assertEqual(join([0, 1, 2], "glue"), "0glue1glue2")

    def test_autoescape(self):
        """
        Tests the `join` function with autoescaping enabled, ensuring that HTML tags are properly escaped.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        - Function: `join`
        - Input: List of strings containing HTML tags
        - Output: Escaped HTML tags separated by '<br>'
        - Keywords: `autoescape`, `join`, `&lt;`, `&gt;`
        """

        self.assertEqual(
            join(["<a>", "<img>", "</a>"], "<br>"),
            "&lt;a&gt;&lt;br&gt;&lt;img&gt;&lt;br&gt;&lt;/a&gt;",
        )

    def test_autoescape_off(self):
        """
        Tests the behavior of the `join` function with `autoescape=False`. The function joins a list of strings with a specified separator, ensuring that no HTML escaping is applied to the result. The expected output is a string where each element from the list is concatenated with the separator, and no HTML entities are converted.
        
        Args:
        None (The test case does not take any arguments).
        
        Returns:
        None (The test case asserts the expected output against the actual output).
        
        Important Functions:
        """

        self.assertEqual(
            join(["<a>", "<img>", "</a>"], "<br>", autoescape=False),
            "<a>&lt;br&gt;<img>&lt;br&gt;</a>",
        )

    def test_noniterable_arg(self):
        obj = object()
        self.assertEqual(join(obj, "<br>"), obj)

    def test_noniterable_arg_autoescape_off(self):
        obj = object()
        self.assertEqual(join(obj, "<br>", autoescape=False), obj)
