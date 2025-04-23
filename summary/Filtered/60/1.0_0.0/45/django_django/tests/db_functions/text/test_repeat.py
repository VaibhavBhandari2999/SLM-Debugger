from django.db import connection
from django.db.models import CharField, Value
from django.db.models.functions import Length, Repeat
from django.test import TestCase

from ..models import Author


class RepeatTests(TestCase):
    def test_basic(self):
        """
        Tests the functionality of the Repeat function in the Author model.
        
        This test case checks how the Repeat function behaves with different inputs and scenarios. It creates an Author instance with the name 'John' and alias 'xyz'. The test then iterates over a series of test cases, each defining a Repeat function with specific parameters. The test asserts that the annotated 'repeated_text' field in the queryset matches the expected repeated text for each case.
        
        Key Parameters:
        - `function`: The Repeat function with specified
        """

        Author.objects.create(name='John', alias='xyz')
        none_value = '' if connection.features.interprets_empty_strings_as_nulls else None
        tests = (
            (Repeat('name', 0), ''),
            (Repeat('name', 2), 'JohnJohn'),
            (Repeat('name', Length('alias'), output_field=CharField()), 'JohnJohnJohn'),
            (Repeat(Value('x'), 3, output_field=CharField()), 'xxx'),
            (Repeat('name', None), none_value),
            (Repeat('goes_by', 1), none_value),
        )
        for function, repeated_text in tests:
            with self.subTest(function=function):
                authors = Author.objects.annotate(repeated_text=function)
                self.assertQuerysetEqual(authors, [repeated_text], lambda a: a.repeated_text, ordered=False)

    def test_negative_number(self):
        with self.assertRaisesMessage(ValueError, "'number' must be greater or equal to 0."):
            Repeat('name', -1)
