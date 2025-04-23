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
        
        This function checks if the NullIf function is raising a TypeError with an appropriate message when called with only one argument instead of the required two.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If NullIf is called with only one argument, the function raises a TypeError with the message "'NullIf' takes exactly 2 arguments (1 given)".
        
        Example:
        >>> with self.assertRaisesMessage(TypeError, msg):
        ...     Null
        """

        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf('name')

    @skipUnless(connection.vendor == 'oracle', 'Oracle specific test for NULL-literal')
    def test_null_literal(self):
        """
        Test for handling null literals in Oracle database queries.
        
        This function tests the behavior of the `NullIf` function when a null literal is used in an expression. Oracle does not allow using `Value(None)` directly in an expression. The function raises a `ValueError` with a specific message if a null literal is used in the `NullIf` function.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - A `ValueError` is raised
        """

        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
