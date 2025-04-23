from django.db import connection
from django.db.models import CharField, Value
from django.db.models.functions import Length, LPad, RPad
from django.test import TestCase

from ..models import Author


class PadTests(TestCase):
    def test_pad(self):
        """
        Tests the functionality of the LPad and RPad functions in the database.
        
        This function creates an author object with the name 'John' and alias 'j'. It then tests various combinations of the LPad and RPad functions to pad the 'name' field with different strings and lengths. The tests include:
        - Padding with a specified string ('xy')
        - Padding with a default space character
        - Truncating the string if it exceeds the specified length
        - Handling of None values
        
        Parameters:
        """

        Author.objects.create(name='John', alias='j')
        none_value = '' if connection.features.interprets_empty_strings_as_nulls else None
        tests = (
            (LPad('name', 7, Value('xy')), 'xyxJohn'),
            (RPad('name', 7, Value('xy')), 'Johnxyx'),
            (LPad('name', 6, Value('x')), 'xxJohn'),
            (RPad('name', 6, Value('x')), 'Johnxx'),
            # The default pad string is a space.
            (LPad('name', 6), '  John'),
            (RPad('name', 6), 'John  '),
            # If string is longer than length it is truncated.
            (LPad('name', 2), 'Jo'),
            (RPad('name', 2), 'Jo'),
            (LPad('name', 0), ''),
            (RPad('name', 0), ''),
            (LPad('name', None), none_value),
            (RPad('name', None), none_value),
            (LPad('goes_by', 1), none_value),
            (RPad('goes_by', 1), none_value),
        )
        for function, padded_name in tests:
            with self.subTest(function=function):
                authors = Author.objects.annotate(padded_name=function)
                self.assertQuerysetEqual(authors, [padded_name], lambda a: a.padded_name, ordered=False)

    def test_pad_negative_length(self):
        """
        Test the padding functions (LPad and RPad) with negative length values.
        
        Parameters:
        function (function): The padding function to test, either LPad or RPad.
        
        This test function checks that both LPad and RPad raise a ValueError when provided with a negative length value. The error message should indicate that the 'length' must be greater than or equal to 0.
        """

        for function in (LPad, RPad):
            with self.subTest(function=function):
                with self.assertRaisesMessage(ValueError, "'length' must be greater or equal to 0."):
                    function('name', -1)

    def test_combined_with_length(self):
        """
        Test the combined functionality of Length and LPad methods on the 'name' and 'alias' fields of the Author model.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Operations:
        - Creates two Author instances with different names and aliases.
        - Annotates the Author queryset with a new field 'filled' using the LPad method, padding the 'name' field with spaces to match the length of the 'alias' field.
        - Orders the queryset by the 'alias' field.
        """

        Author.objects.create(name='Rhonda', alias='john_smith')
        Author.objects.create(name='♥♣♠', alias='bytes')
        authors = Author.objects.annotate(filled=LPad('name', Length('alias'), output_field=CharField()))
        self.assertQuerysetEqual(
            authors.order_by('alias'),
            ['  ♥♣♠', '    Rhonda'],
            lambda a: a.filled,
        )
