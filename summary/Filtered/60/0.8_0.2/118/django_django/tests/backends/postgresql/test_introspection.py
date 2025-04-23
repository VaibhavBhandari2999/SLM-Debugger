import unittest

from django.db import connection
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == "postgresql", "Test only for PostgreSQL")
class DatabaseSequenceTests(TestCase):
    def test_get_sequences(self):
        """
        Tests the retrieval of database sequences for a specific model table.
        
        This function checks the ability to fetch database sequences for a given model table. It uses a cursor to interact with the database and fetches the sequences for the specified table. The function first retrieves the sequences and asserts that the sequence name is as expected. Then, it renames the sequence and retrieves the sequences again to verify that the new name is correctly fetched.
        
        Parameters:
        - cursor: A database cursor object used to execute SQL queries.
        
        Returns
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
        )
