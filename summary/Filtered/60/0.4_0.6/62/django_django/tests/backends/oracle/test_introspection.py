import unittest

from django.db import connection
from django.test import TransactionTestCase

from ..models import Square


@unittest.skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class DatabaseSequenceTests(TransactionTestCase):
    available_apps = []

    def test_get_sequences(self):
        """
        Tests the get_sequences method to ensure it correctly retrieves sequence information for a specified model's table.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the length of the sequences list is not 1, or if the sequence details do not match the expected values.
        
        Key Parameters:
        - `cursor`: A database cursor used to execute the SQL query.
        - `Square._meta.db_table`: The database table name for the Square model.
        - `Square._meta
        """

        with connection.cursor() as cursor:
            seqs = connection.introspection.get_sequences(cursor, Square._meta.db_table, Square._meta.local_fields)
            self.assertEqual(len(seqs), 1)
            self.assertIsNotNone(seqs[0]['name'])
            self.assertEqual(seqs[0]['table'], Square._meta.db_table)
            self.assertEqual(seqs[0]['column'], 'id')

    def test_get_sequences_manually_created_index(self):
        with connection.cursor() as cursor:
            with connection.schema_editor() as editor:
                editor._drop_identity(Square._meta.db_table, 'id')
                seqs = connection.introspection.get_sequences(cursor, Square._meta.db_table, Square._meta.local_fields)
                self.assertEqual(seqs, [{'table': Square._meta.db_table, 'column': 'id'}])
                # Recreate model, because adding identity is impossible.
                editor.delete_model(Square)
                editor.create_model(Square)
