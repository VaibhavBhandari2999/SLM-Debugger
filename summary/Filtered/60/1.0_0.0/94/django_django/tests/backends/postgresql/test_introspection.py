import unittest

from django.db import connection
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == "postgresql", "Test only for PostgreSQL")
class DatabaseSequenceTests(TestCase):
    def test_get_sequences(self):
        """
        Function: test_get_sequences
        
        This function tests the retrieval of database sequences for a specific model's table.
        
        Parameters:
        - cursor: A database cursor object used to execute SQL commands.
        
        Returns:
        - None: This function does not return any value. It asserts the correctness of the sequences retrieved.
        
        Description:
        The function first retrieves the sequences for the specified model's table and asserts that the sequence name is as expected. Then, it renames the sequence and retrieves the sequences again to assert the new sequence
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
        Tests the retrieval of sequences for a specific table.
        
        This function creates a temporary table named 'testing' with a SERIAL column and then uses the `get_sequences` method from the database connection's introspection module to retrieve the sequence information for that column. The expected result is a list containing a dictionary with the table name, column name, and the sequence name.
        
        Parameters:
        - cursor (cursor): A database cursor object used to execute SQL commands.
        
        Returns:
        - list: A list of dictionaries, each
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
