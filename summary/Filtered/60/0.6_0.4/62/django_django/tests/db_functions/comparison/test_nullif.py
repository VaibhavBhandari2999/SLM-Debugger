from unittest import skipUnless

from django.db import connection
from django.db.models import Value
from django.db.models.functions import NullIf
from django.test import TestCase

from ..models import Author


class NullIfTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda', alias='Rhonda')

    def test_basic(self):
        """
        Tests the basic functionality of the NullIf function in a database query.
        
        This test checks how the NullIf function behaves when applied to the 'alias' and 'name' fields of the Author model. The function is used to replace the 'alias' field with 'None' if it matches the 'name' field. The result is then compared against a predefined list of expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Expected Output:
        A sequence of tuples, where each tuple contains
        """

        authors = Author.objects.annotate(nullif=NullIf('alias', 'name')).values_list('nullif')
        self.assertSequenceEqual(
            authors, [
                ('smithj',),
                ('' if connection.features.interprets_empty_strings_as_nulls else None,)
            ]
        )

    def test_null_argument(self):
        authors = Author.objects.annotate(nullif=NullIf('name', Value(None))).values_list('nullif')
        self.assertSequenceEqual(authors, [('John Smith',), ('Rhonda',)])

    def test_too_few_args(self):
        """
        Test the NullIf function with insufficient arguments.
        
        This function checks if the NullIf function raises a TypeError when it is called with only one argument instead of the required two. The expected error message is "'NullIf' takes exactly 2 arguments (1 given)".
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the NullIf function is called with one argument instead of two, the function will raise a TypeError with the message "'NullIf' takes exactly 2 arguments
        """

        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf('name')

    @skipUnless(connection.vendor == 'oracle', 'Oracle specific test for NULL-literal')
    def test_null_literal(self):
        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
