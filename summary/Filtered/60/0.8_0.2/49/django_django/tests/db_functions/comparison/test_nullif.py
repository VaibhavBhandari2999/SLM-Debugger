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
        Tests the basic functionality of the NullIf function in the Author model.
        
        This test checks the output of the NullIf function, which is used to return the first argument if the two arguments are not equal, otherwise it returns NULL. The function is applied to the 'alias' and 'name' fields of the Author model and the result is compared against expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Expected Output:
        A sequence of tuples, where each tuple contains the result of the
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
        Test the NullIf function with too few arguments.
        
        This function checks that the NullIf function raises a TypeError with an appropriate message when called with only one argument.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If NullIf is called with less than 2 arguments.
        
        Example:
        >>> with self.assertRaisesMessage(TypeError, msg):
        ...     NullIf('name')
        ...
        TypeError: 'NullIf' takes exactly 2 arguments (1 given)
        """

        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf('name')

    @skipUnless(connection.vendor == 'oracle', 'Oracle specific test for NULL-literal')
    def test_null_literal(self):
        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
