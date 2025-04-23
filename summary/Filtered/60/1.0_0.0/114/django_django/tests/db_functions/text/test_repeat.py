from django.db import connection
from django.db.models import Value
from django.db.models.functions import Length, Repeat
from django.test import TestCase

from ..models import Author


class RepeatTests(TestCase):
    def test_basic(self):
        """
        Tests the functionality of the Repeat function in a database query.
        
        This function creates an author with the name "John" and alias "xyz". It then tests the Repeat function with various inputs to ensure it behaves as expected. The Repeat function is used to repeat a given field or value a specified number of times. The test cases include:
        
        - Repeating the 'name' field 0 times.
        - Repeating the 'name' field 2 times.
        - Repeating the 'name' field a
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
        """
        Test that a negative number is not accepted for the 'number' parameter.
        
        Args:
        None
        
        Raises:
        ValueError: If 'number' is less than 0, the function raises a ValueError with the message "'number' must be greater or equal to 0."
        
        Note:
        The function checks if the 'number' parameter is a negative integer and raises an appropriate error message if it is.
        """

        with self.assertRaisesMessage(
            ValueError, "'number' must be greater or equal to 0."
        ):
            Repeat("name", -1)
