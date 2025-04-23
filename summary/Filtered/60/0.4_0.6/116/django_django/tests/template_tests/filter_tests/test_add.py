from datetime import date, timedelta

from django.template.defaultfilters import add
from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy

from ..utils import setup


class AddTests(SimpleTestCase):
    """
    Tests for #11687 and #16676
    """

    @setup({"add01": '{{ i|add:"5" }}'})
    def test_add01(self):
        output = self.engine.render_to_string("add01", {"i": 2000})
        self.assertEqual(output, "2005")

    @setup({"add02": '{{ i|add:"napis" }}'})
    def test_add02(self):
        output = self.engine.render_to_string("add02", {"i": 2000})
        self.assertEqual(output, "")

    @setup({"add03": "{{ i|add:16 }}"})
    def test_add03(self):
        output = self.engine.render_to_string("add03", {"i": "not_an_int"})
        self.assertEqual(output, "")

    @setup({"add04": '{{ i|add:"16" }}'})
    def test_add04(self):
        output = self.engine.render_to_string("add04", {"i": "not_an_int"})
        self.assertEqual(output, "not_an_int16")

    @setup({"add05": "{{ l1|add:l2 }}"})
    def test_add05(self):
        output = self.engine.render_to_string("add05", {"l1": [1, 2], "l2": [3, 4]})
        self.assertEqual(output, "[1, 2, 3, 4]")

    @setup({"add06": "{{ t1|add:t2 }}"})
    def test_add06(self):
        output = self.engine.render_to_string("add06", {"t1": (3, 4), "t2": (1, 2)})
        self.assertEqual(output, "(3, 4, 1, 2)")

    @setup({"add07": "{{ d|add:t }}"})
    def test_add07(self):
        """
        Test rendering a template with a date and timedelta context.
        
        This function tests the rendering of a template named 'add07' with a context
        containing a date object 'd' and a timedelta object 't'. The date object is
        set to January 1, 2000, and the timedelta object is set to 10 days. The
        expected output is a string representing the date 10 days after the given
        date, formatted as "Month. Day,
        """

        output = self.engine.render_to_string(
            "add07", {"d": date(2000, 1, 1), "t": timedelta(10)}
        )
        self.assertEqual(output, "Jan. 11, 2000")

    @setup({"add08": "{{ s1|add:lazy_s2 }}"})
    def test_add08(self):
        output = self.engine.render_to_string(
            "add08",
            {"s1": "string", "lazy_s2": gettext_lazy("lazy")},
        )
        self.assertEqual(output, "stringlazy")

    @setup({"add09": "{{ lazy_s1|add:lazy_s2 }}"})
    def test_add09(self):
        output = self.engine.render_to_string(
            "add09",
            {"lazy_s1": gettext_lazy("string"), "lazy_s2": gettext_lazy("lazy")},
        )
        self.assertEqual(output, "stringlazy")


class FunctionTests(SimpleTestCase):
    def test_add(self):
        self.assertEqual(add("1", "2"), 3)
ctionTests(SimpleTestCase):
    def test_add(self):
        self.assertEqual(add("1", "2"), 3)
