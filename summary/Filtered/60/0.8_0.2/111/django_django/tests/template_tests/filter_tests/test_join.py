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
        Tests the rendering of a template with a join operation and custom separator.
        
        This function tests the `render_to_string` method of the `engine` object with a template named "join05". The template is expected to use the `join` operation to concatenate the elements of the list `a` with the separator `var`. The list `a` contains strings that may include special characters that need to be properly escaped in the output. The separator `var` is a string containing special characters that
        """

        output = self.engine.render_to_string(
            "join05", {"a": ["alpha", "beta & me"], "var": " & "}
        )
        self.assertEqual(output, "alpha &amp; beta &amp; me")

    @setup({"join06": "{{ a|join:var }}"})
    def test_join06(self):
        """
        Tests the rendering of a template with a join operation. The template is expected to join elements of a list with a given separator.
        The function takes a Django template engine instance, a template name ("join06"), and a context dictionary as input.
        The context dictionary contains a list 'a' with elements "alpha", "beta & me", and a 'var' with a marked safe separator " & ".
        The function renders the template and asserts that the output is "alpha & beta
        """

        output = self.engine.render_to_string(
            "join06", {"a": ["alpha", "beta & me"], "var": mark_safe(" & ")}
        )
        self.assertEqual(output, "alpha & beta &amp; me")

    @setup({"join07": "{{ a|join:var|lower }}"})
    def test_join07(self):
        output = self.engine.render_to_string(
            "join07", {"a": ["Alpha", "Beta & me"], "var": " & "}
        )
        self.assertEqual(output, "alpha &amp; beta &amp; me")

    @setup({"join08": "{{ a|join:var|lower }}"})
    def test_join08(self):
        output = self.engine.render_to_string(
            "join08", {"a": ["Alpha", "Beta & me"], "var": mark_safe(" & ")}
        )
        self.assertEqual(output, "alpha & beta &amp; me")


class FunctionTests(SimpleTestCase):
    def test_list(self):
        self.assertEqual(join([0, 1, 2], "glue"), "0glue1glue2")

    def test_autoescape(self):
        self.assertEqual(
            join(["<a>", "<img>", "</a>"], "<br>"),
            "&lt;a&gt;&lt;br&gt;&lt;img&gt;&lt;br&gt;&lt;/a&gt;",
        )

    def test_autoescape_off(self):
        """
        Tests the behavior of the `join` function when `autoescape` is set to `False`.
        
        Parameters:
        - `parts` (list): A list of strings to be joined.
        - `separator` (str): The separator to use between the strings in the list.
        
        Keyword Arguments:
        - `autoescape` (bool): If `False`, HTML entities are not escaped. Default is `False`.
        
        Returns:
        - str: The joined string with the separator between each part, without escaping HTML entities
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
tEqual(join(obj, "<br>", autoescape=False), obj)
