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
        
        This test checks that the NullIf function raises a TypeError with an appropriate message when called with fewer than two arguments.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If NullIf is called with fewer than two arguments, a TypeError is raised with the message "'NullIf' takes exactly 2 arguments (1 given)".
        """

        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf('name')

    @skipUnless(connection.vendor == 'oracle', 'Oracle specific test for NULL-literal')
    def test_null_literal(self):
        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
        
        This function checks if Oracle raises a ValueError when attempting to use a null literal with the NullIf function. The expected behavior is that Oracle does not allow Value(None) for expression1 in the NullIf function, and this test case verifies that a ValueError is raised with the appropriate message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the test case does not raise a
        """

        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
