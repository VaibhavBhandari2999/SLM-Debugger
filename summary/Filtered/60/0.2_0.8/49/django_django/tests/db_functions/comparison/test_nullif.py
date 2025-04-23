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
        
        This test checks the behavior of the NullIf function, which returns the first argument if both arguments are not null, otherwise it returns the second argument. The function is applied to the 'alias' and 'name' fields of the Author model and the results are stored in the 'nullif' field. The test asserts that the resulting list of 'nullif' values matches the expected output, which depends on whether the database interpre
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
        Tests the behavior of the NullIf function when applied to a null literal in an Oracle database.
        
        This function checks if Oracle raises a ValueError when attempting to use None as a value in a NullIf expression. The NullIf function is used to return the first argument if it is not equal to the second argument; otherwise, it returns None. In this case, the function attempts to use None as the first argument, which is not allowed in Oracle.
        
        Parameters:
        None
        
        Returns:
        None
        """

        msg = 'Oracle does not allow Value(None) for expression1.'
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(nullif=NullIf(Value(None), 'name')).values_list('nullif'))
