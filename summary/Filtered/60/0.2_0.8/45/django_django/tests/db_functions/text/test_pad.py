from django.db import connection
from django.db.models import CharField, Value
from django.db.models.functions import Length, LPad, RPad
from django.test import TestCase

from ..models import Author


class PadTests(TestCase):
    def test_pad(self):
        """
        Tests the functionality of the LPad and RPad string manipulation functions in a database query context.
        
        This function creates an author object with a specific name and alias. It then tests various scenarios of the LPad and RPad functions, which are used to pad strings to a specified length with a given padding character. The tests include different lengths, default padding characters, and handling of None values. The function returns a queryset of annotated authors with their padded names.
        
        Parameters:
        - None (The function uses predefined
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
        for function in (LPad, RPad):
            with self.subTest(function=function):
                with self.assertRaisesMessage(ValueError, "'length' must be greater or equal to 0."):
                    function('name', -1)

    def test_combined_with_length(self):
        """
        Test the combined functionality of Length and LPad on the 'name' and 'alias' fields of the Author model.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Operations:
        - Creates two Author objects with different 'name' and 'alias' values.
        - Annotates the Author queryset with a new field 'filled' using LPad to pad the 'name' field with spaces to match the length of the 'alias' field.
        - Orders the queryset by 'alias' and
        """

        Author.objects.create(name='Rhonda', alias='john_smith')
        Author.objects.create(name='♥♣♠', alias='bytes')
        authors = Author.objects.annotate(filled=LPad('name', Length('alias'), output_field=CharField()))
        self.assertQuerysetEqual(
            authors.order_by('alias'),
            ['  ♥♣♠', '    Rhonda'],
            lambda a: a.filled,
        )
