from decimal import Decimal

from django.template.defaultfilters import pluralize
from django.test import SimpleTestCase

from ..utils import setup


class PluralizeTests(SimpleTestCase):
    def check_values(self, *tests):
        for value, expected in tests:
            with self.subTest(value=value):
                output = self.engine.render_to_string("t", {"value": value})
                self.assertEqual(output, expected)

    @setup({"t": "vote{{ value|pluralize }}"})
    def test_no_arguments(self):
        self.check_values(("0", "votes"), ("1", "vote"), ("2", "votes"))

    @setup({"t": 'class{{ value|pluralize:"es" }}'})
    def test_suffix(self):
        self.check_values(("0", "classes"), ("1", "class"), ("2", "classes"))

    @setup({"t": 'cand{{ value|pluralize:"y,ies" }}'})
    def test_singular_and_plural_suffix(self):
        self.check_values(("0", "candies"), ("1", "candy"), ("2", "candies"))


class FunctionTests(SimpleTestCase):
    def test_integers(self):
        self.assertEqual(pluralize(1), "")
        self.assertEqual(pluralize(0), "s")
        self.assertEqual(pluralize(2), "s")

    def test_floats(self):
        self.assertEqual(pluralize(0.5), "s")
        self.assertEqual(pluralize(1.5), "s")

    def test_decimals(self):
        self.assertEqual(pluralize(Decimal(1)), "")
        self.assertEqual(pluralize(Decimal(0)), "s")
        self.assertEqual(pluralize(Decimal(2)), "s")

    def test_lists(self):
        """
        Tests the pluralize function with different list inputs.
        
        Args:
        self: The instance of the test class.
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output of the pluralize function does not match the expected result.
        
        Parameters:
        None
        
        Key Behavior:
        - Checks if the pluralize function returns an empty string for a single-element list.
        - Verifies that the pluralize function returns 's' for an empty list.
        - Ensures that the pluralize function returns 's
        """

        self.assertEqual(pluralize([1]), "")
        self.assertEqual(pluralize([]), "s")
        self.assertEqual(pluralize([1, 2, 3]), "s")

    def test_suffixes(self):
        """
        Test the pluralize function.
        
        Args:
        num (int): The number to determine the plural form.
        suffixes (str): A comma-separated string of suffixes to use for singular and plural forms.
        
        Returns:
        str: The appropriate suffix based on the number provided.
        
        Test cases:
        - `pluralize(1, "es")` should return an empty string.
        - `pluralize(0, "es")` should return "es".
        - `pluralize(2, "
        """

        self.assertEqual(pluralize(1, "es"), "")
        self.assertEqual(pluralize(0, "es"), "es")
        self.assertEqual(pluralize(2, "es"), "es")
        self.assertEqual(pluralize(1, "y,ies"), "y")
        self.assertEqual(pluralize(0, "y,ies"), "ies")
        self.assertEqual(pluralize(2, "y,ies"), "ies")
        self.assertEqual(pluralize(0, "y,ies,error"), "")

    def test_no_len_type(self):
        self.assertEqual(pluralize(object(), "y,es"), "")
        self.assertEqual(pluralize(object(), "es"), "")

    def test_value_error(self):
        self.assertEqual(pluralize("", "y,es"), "")
        self.assertEqual(pluralize("", "es"), "")
