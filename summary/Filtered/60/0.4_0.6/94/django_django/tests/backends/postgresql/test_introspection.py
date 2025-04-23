import unittest

from django.db import connection
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == "postgresql", "Test only for PostgreSQL")
class DatabaseSequenceTests(TestCase):
    def test_get_sequences(self):
        """
        Tests the get_sequences method of the database introspection.
        
        This method retrieves the sequence information for a given table. The function first queries the database to get the sequences for the specified table and asserts that the sequence name is 'backends_person_id_seq'. Then, it renames the sequence to 'pers_seq' and rechecks the sequence information to ensure that the new name is correctly reflected.
        
        Parameters:
        - cursor: A database cursor object used to execute SQL queries.
        
        Returns:
        - None: This function
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
        
        This function creates a temporary table named 'testing' with a SERIAL column. It then retrieves the sequence information for this column using the `get_sequences` method from the connection's introspection module. The expected output is a list containing a dictionary with the table name, column name, and sequence name.
        
        Parameters:
        - cursor: A database cursor object used to execute SQL commands.
        
        Returns:
        - A list of dictionaries, each representing a sequence for a column
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
