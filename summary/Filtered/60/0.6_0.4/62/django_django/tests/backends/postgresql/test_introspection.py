import unittest

from django.db import connection
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == 'postgresql', "Test only for PostgreSQL")
class DatabaseSequenceTests(TestCase):
    def test_get_sequences(self):
        """
        Tests the get_sequences method of the database introspection.
        
        This method retrieves the sequences used for auto-incrementing fields in a specified table. The test first fetches the sequences for the 'Person' model's table and checks if the sequence name is as expected. Then, it renames the sequence and re-fetches the sequences to verify that the new name is correctly returned.
        
        Parameters:
        - cursor: A database cursor object used to execute SQL queries.
        
        Returns:
        - None: This function does not
        """

        with connection.cursor() as cursor:
            seqs = connection.introspection.get_sequences(cursor, Person._meta.db_table)
            self.assertEqual(
                seqs,
                [{'table': Person._meta.db_table, 'column': 'id', 'name': 'backends_person_id_seq'}]
            )
            cursor.execute('ALTER SEQUENCE backends_person_id_seq RENAME TO pers_seq')
            seqs = connection.introspection.get_sequences(cursor, Person._meta.db_table)
            self.assertEqual(
                seqs,
                [{'table': Person._meta.db_table, 'column': 'id', 'name': 'pers_seq'}]
            )
