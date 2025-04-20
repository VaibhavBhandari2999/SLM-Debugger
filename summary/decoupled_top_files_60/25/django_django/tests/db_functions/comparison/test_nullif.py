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
        Tests the basic functionality of the NullIf annotation in the Author model.
        
        This function checks the output of the NullIf annotation on the 'alias' and 'name' fields of the Author model. It uses the `annotate` method to apply the NullIf function and then retrieves the results using `values_list`. The expected output is a sequence of tuples, where each tuple contains the result of the NullIf operation. The test verifies that the output matches the expected values, taking into account whether the database
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
        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf('name')

    @skipUnless(connection.vendor == 'oracle', 'Oracle specific test for NULL-literal')
    def test_null_literal(self):
        """
        Tests the behavior of the `NullIf` function when a `None` value is used as the first argument.
        
        This function checks if Oracle raises a `ValueError` with a specific message when attempting to use `None` as the first argument in the `NullIf` function. The `NullIf` function is used to return `None` if the first argument is `None` or equal to the second argument.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError:
        """

        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
