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
        
        This test checks the behavior of the NullIf function on the 'alias' and 'name' fields of the Author model. It uses the annotate method to apply the NullIf function and then retrieves the results using values_list. The expected output is a sequence of tuples, where each tuple contains the result of the NullIf function for each author. The test also takes into account the feature of the database connection that interprets empty strings
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
        Tests the behavior of the NullIf function when a null literal is used in an expression.
        
        This function checks if Oracle raises a ValueError when attempting to use a null literal with the NullIf function. The expected behavior is that Oracle will not allow this and will raise a ValueError with a specific message.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function will raise a ValueError with the message: 'Oracle does not allow Value(None) for expression1.'
        """

        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
