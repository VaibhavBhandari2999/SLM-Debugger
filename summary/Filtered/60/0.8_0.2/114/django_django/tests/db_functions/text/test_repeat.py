from django.db import connection
from django.db.models import Value
from django.db.models.functions import Length, Repeat
from django.test import TestCase

from ..models import Author


class RepeatTests(TestCase):
    def test_basic(self):
        """
        Tests the functionality of the Repeat function in the context of the Author model.
        
        This test function creates an Author object with the name "John" and alias "xyz". It then tests the Repeat function with various inputs to ensure it behaves as expected. The Repeat function is used to repeat a given value a specified number of times.
        
        Parameters:
        - None (This function uses internal data and does not take any parameters).
        
        Returns:
        - None (This function asserts the correctness of the Repeat function's output through internal
        """

        Author.objects.create(name="John", alias="xyz")
        none_value = (
            "" if connection.features.interprets_empty_strings_as_nulls else None
        )
        tests = (
            (Repeat("name", 0), ""),
            (Repeat("name", 2), "JohnJohn"),
            (Repeat("name", Length("alias")), "JohnJohnJohn"),
            (Repeat(Value("x"), 3), "xxx"),
            (Repeat("name", None), none_value),
            (Repeat(Value(None), 4), none_value),
            (Repeat("goes_by", 1), none_value),
        )
        for function, repeated_text in tests:
            with self.subTest(function=function):
                authors = Author.objects.annotate(repeated_text=function)
                self.assertQuerySetEqual(
                    authors, [repeated_text], lambda a: a.repeated_text, ordered=False
                )

    def test_negative_number(self):
        with self.assertRaisesMessage(
            ValueError, "'number' must be greater or equal to 0."
        ):
            Repeat("name", -1)
