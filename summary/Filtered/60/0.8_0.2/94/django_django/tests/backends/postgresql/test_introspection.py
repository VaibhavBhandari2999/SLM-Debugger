import unittest

from django.db import connection
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == "postgresql", "Test only for PostgreSQL")
class DatabaseSequenceTests(TestCase):
    def test_get_sequences(self):
        """
        Tests the get_sequences method of the database introspection.
        
        This method retrieves the sequences used for auto-incrementing columns in a specified table. The function first queries the database to get the sequences for the 'Person' table and checks if the sequences are correctly identified. Then, it renames the sequence and rechecks to ensure the method correctly updates the sequence name.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Connect to the database and retrieve the sequences for the 'Person
        """

        with connection.cursor() as cursor:
            seqs = connection.introspection.get_sequences(cursor, Person._meta.db_table)
            self.assertEqual(
                seqs,
                [
                    {
                        "table": Person._meta.db_table,
                        "column": "id",
                        "name": "backends_person_id_seq",
                    }
                ],
            )
            cursor.execute("ALTER SEQUENCE backends_person_id_seq RENAME TO pers_seq")
            seqs = connection.introspection.get_sequences(cursor, Person._meta.db_table)
            self.assertEqual(
                seqs,
                [{"table": Person._meta.db_table, "column": "id", "name": "pers_seq"}],
            )

    def test_get_sequences_old_serial(self):
        """
        Tests the `get_sequences` function for retrieving sequences from a database.
        
        This function creates a temporary table named 'testing' with a serial field. It then uses the `get_sequences` function to retrieve the sequence information for the serial field. The expected result is a list containing a dictionary with the table name, column name, and sequence name.
        
        Parameters:
        - No external parameters are passed to this function.
        
        Returns:
        - A list of dictionaries, each representing a sequence. The dictionary contains the keys '
        """

        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE testing (serial_field SERIAL);")
            seqs = connection.introspection.get_sequences(cursor, "testing")
            self.assertEqual(
                seqs,
                [
                    {
                        "table": "testing",
                        "column": "serial_field",
                        "name": "testing_serial_field_seq",
                    }
                ],
            )
