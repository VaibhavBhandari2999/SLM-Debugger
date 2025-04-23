import unittest

from django.db import connection
from django.test import TransactionTestCase

from ..models import Square


@unittest.skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class DatabaseSequenceTests(TransactionTestCase):
    available_apps = []

    def test_get_sequences(self):
        """
        Tests the get_sequences method of the database introspection.
        
        This method retrieves the sequences for a specific table and its fields. The function connects to the database, fetches the sequences for the 'Square' table, and verifies the correctness of the returned sequences.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The length of the sequences list is 1.
        - The sequence name is not None.
        - The sequence table is 'Square'.
        - The sequence column is '
        """

        with connection.cursor() as cursor:
            seqs = connection.introspection.get_sequences(cursor, Square._meta.db_table, Square._meta.local_fields)
            self.assertEqual(len(seqs), 1)
            self.assertIsNotNone(seqs[0]['name'])
            self.assertEqual(seqs[0]['table'], Square._meta.db_table)
            self.assertEqual(seqs[0]['column'], 'id')

    def test_get_sequences_manually_created_index(self):
        """
        Tests the manual creation and introspection of sequences for a model's primary key.
        
        This function drops the identity column for a given model's table, then retrieves the sequences associated with that table using the database's introspection methods. It asserts that the retrieved sequences include the specified primary key column. After the test, the model is deleted and recreated to restore the identity column.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Drops the identity column for the specified model's table.
        """

        with connection.cursor() as cursor:
            with connection.schema_editor() as editor:
                editor._drop_identity(Square._meta.db_table, 'id')
                seqs = connection.introspection.get_sequences(cursor, Square._meta.db_table, Square._meta.local_fields)
                self.assertEqual(seqs, [{'table': Square._meta.db_table, 'column': 'id'}])
                # Recreate model, because adding identity is impossible.
                editor.delete_model(Square)
                editor.create_model(Square)
