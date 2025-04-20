import datetime

from django.db import connection
from django.test import TestCase, skipUnlessDBFeature
from django.test.utils import CaptureQueriesContext

from .models import DumbCategory, NonIntegerPKReturningModel, ReturningModel


@skipUnlessDBFeature('can_return_columns_from_insert')
class ReturningValuesTests(TestCase):
    def test_insert_returning(self):
        """
        Tests the behavior of the `create` method on a Django model instance to ensure that it includes a RETURNING clause in the generated SQL query. The function captures the SQL queries using a context manager and checks if the last query contains the expected RETURNING clause for the primary key of the model.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Raises:
        - AssertionError: If the generated SQL query does not contain the expected RETURNING clause.
        """

        with CaptureQueriesContext(connection) as captured_queries:
            DumbCategory.objects.create()
        self.assertIn(
            'RETURNING %s.%s' % (
                connection.ops.quote_name(DumbCategory._meta.db_table),
                connection.ops.quote_name(DumbCategory._meta.get_field('id').column),
            ),
            captured_queries[-1]['sql'],
        )

    def test_insert_returning_non_integer(self):
        obj = NonIntegerPKReturningModel.objects.create()
        self.assertTrue(obj.created)
        self.assertIsInstance(obj.created, datetime.datetime)

    def test_insert_returning_multiple(self):
        """
        Tests the `test_insert_returning_multiple` method.
        
        This test checks if the `RETURNING` clause is correctly used in an insert operation to retrieve multiple fields. The test creates an instance of `ReturningModel` and verifies that the `RETURNING` clause is included in the SQL query. It also ensures that the object's primary key and created timestamp are correctly set.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The test uses a `CaptureQueriesContext` to capture
        """

        with CaptureQueriesContext(connection) as captured_queries:
            obj = ReturningModel.objects.create()
        table_name = connection.ops.quote_name(ReturningModel._meta.db_table)
        self.assertIn(
            'RETURNING %s.%s, %s.%s' % (
                table_name,
                connection.ops.quote_name(ReturningModel._meta.get_field('id').column),
                table_name,
                connection.ops.quote_name(ReturningModel._meta.get_field('created').column),
            ),
            captured_queries[-1]['sql'],
        )
        self.assertTrue(obj.pk)
        self.assertIsInstance(obj.created, datetime.datetime)

    @skipUnlessDBFeature('can_return_rows_from_bulk_insert')
    def test_bulk_insert(self):
        objs = [ReturningModel(), ReturningModel(pk=2 ** 11), ReturningModel()]
        ReturningModel.objects.bulk_create(objs)
        for obj in objs:
            with self.subTest(obj=obj):
                self.assertTrue(obj.pk)
                self.assertIsInstance(obj.created, datetime.datetime)
