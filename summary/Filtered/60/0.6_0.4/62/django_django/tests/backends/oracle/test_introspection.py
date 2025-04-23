import unittest

from django.db import connection
from django.test import TransactionTestCase

from ..models import Square


@unittest.skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class DatabaseSequenceTests(TransactionTestCase):
    available_apps = []

    def test_get_sequences(self):
        """
        Tests the get_sequences method for a specific table and its local fields.
        
        This function connects to the database and retrieves the sequences associated with the specified table. It then checks the length of the returned sequences, ensures that the sequence name is not None, and verifies that the table and column names match the expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - connection: The database connection used to retrieve the sequences.
        - Square._meta.db_table: The database table name for
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
        
        This function drops the identity column for the 'Square' model, retrieves the sequences for the specified table and column, and asserts that the sequence is correctly identified. It then deletes and recreates the model to ensure the identity column is properly re-established.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Steps:
        1. Drops the identity column for the 'Square' model.
        2. Retrieves the sequences for the 'Square
        """

        with connection.cursor() as cursor:
            with connection.schema_editor() as editor:
                editor._drop_identity(Square._meta.db_table, 'id')
                seqs = connection.introspection.get_sequences(cursor, Square._meta.db_table, Square._meta.local_fields)
                self.assertEqual(seqs, [{'table': Square._meta.db_table, 'column': 'id'}])
                # Recreate model, because adding identity is impossible.
                editor.delete_model(Square)
                editor.create_model(Square)
