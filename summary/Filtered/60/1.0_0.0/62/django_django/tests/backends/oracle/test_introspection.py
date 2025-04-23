import unittest

from django.db import connection
from django.test import TransactionTestCase

from ..models import Square


@unittest.skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class DatabaseSequenceTests(TransactionTestCase):
    available_apps = []

    def test_get_sequences(self):
        """
        Function to test the retrieval of database sequences for a specific model.
        
        Args:
        None
        
        Returns:
        None
        
        This function executes a database query to retrieve the sequences used for auto-incrementing the 'id' field of the 'Square' model. It then asserts that the sequence information is correctly retrieved and formatted.
        
        Key Parameters:
        - `cursor`: A database cursor used to execute the introspection query.
        - `table_name`: The name of the database table associated with the 'Square' model
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
model(Square)
