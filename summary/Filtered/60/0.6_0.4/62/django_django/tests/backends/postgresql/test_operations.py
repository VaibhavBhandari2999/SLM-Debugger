import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import SimpleTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == 'postgresql', 'PostgreSQL tests.')
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Test SQL flush operation.
        
        This function checks the SQL flush command for specified database tables. The `sql_flush` method is called with the no style context and a list of table names. The expected output is a list of SQL commands to truncate the specified tables.
        
        Parameters:
        no_style (callable): A context function that returns a no style instance.
        table_list (list): A list of table names to be flushed.
        
        Returns:
        list: A list of SQL commands to truncate the specified tables
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
            ),
            ['TRUNCATE "backends_person", "backends_tag";'],
        )

    def test_sql_flush_allow_cascade(self):
        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                allow_cascade=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" CASCADE;'],
        )

    def test_sql_flush_sequences(self):
        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY;'],
        )

    def test_sql_flush_sequences_allow_cascade(self):
        """
        Test SQL flush sequences with cascade.
        
        This function generates SQL commands to flush sequences for specified database tables, allowing cascading operations. The function takes the following parameters:
        - no_style: A function that returns a style object for database operations.
        - table_list: A list of table names to be flushed.
        - reset_sequences: A boolean indicating whether to reset sequences after flushing tables (default is True).
        - allow_cascade: A boolean indicating whether to allow cascading operations during the flush (default is True
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
                allow_cascade=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY CASCADE;'],
        )
