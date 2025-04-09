"""
The provided Python file contains unit tests for database operations using Django's SQLite backend. Specifically, it focuses on testing the `sql_flush` method of the `BaseDatabaseOperations` class, which is responsible for generating SQL commands to flush (delete) data from specified database tables. The tests cover different scenarios such as flushing without cascading, with cascading, resetting sequences, and resetting sequences with cascading. Each test method ensures that the generated SQL commands match the expected output by comparing them against predefined lists of SQL statements. The tests are designed to validate the correctness of the SQL generation logic under various conditions. ```python
"""
import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import TestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class SQLiteOperationsTests(TestCase):
    def test_sql_flush(self):
        """
        Test the SQL flush operation.
        
        This function checks if the SQL flush command, when executed with the
        specified database tables (`Person._meta.db_table` and `Tag._meta.db_table`),
        generates the expected SQL delete statements.
        
        Args:
        None
        
        Returns:
        list: A list of SQL delete statements.
        
        Important Functions:
        - `connection.ops.sql_flush`: Generates SQL commands to flush (delete) data from specified tables.
        - `no_style()`: Returns
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
            ),
            [
                'DELETE FROM "backends_person";',
                'DELETE FROM "backends_tag";',
            ],
        )

    def test_sql_flush_allow_cascade(self):
        """
        Flushes the specified database tables with cascading deletes.
        
        Args:
        no_style (bool): Whether to use the database's default output formatting.
        table_names (list): List of table names to be flushed.
        allow_cascade (bool): Whether to allow cascading deletes during the flush operation.
        
        Returns:
        list: A list of SQL statements to be executed for flushing the specified tables.
        
        Example:
        >>> statements = connection.ops.sql_flush(no_style=False, table_names=['
        """

        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
            allow_cascade=True,
        )
        self.assertEqual(
            # The tables are processed in an unordered set.
            sorted(statements),
            [
                'DELETE FROM "backends_person";',
                'DELETE FROM "backends_tag";',
                'DELETE FROM "backends_verylongmodelnamezzzzzzzzzzzzzzzzzzzzzz'
                'zzzzzzzzzzzzzzzzzzzz_m2m_also_quite_long_zzzzzzzzzzzzzzzzzzzz'
                'zzzzzzzzzzzzzzzzzzzzzzz";',
            ],
        )

    def test_sql_flush_sequences(self):
        """
        Flush sequences for specified database tables.
        
        Args:
        no_style (BaseDatabaseOperations.no_style): A method that returns
        a style context manager with no styling enabled.
        table_names (list): List of table names to flush, including their
        respective meta data.
        
        Returns:
        list: SQL commands to delete data and reset sequences for the given
        tables.
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
            ),
            [
                'DELETE FROM "backends_person";',
                'DELETE FROM "backends_tag";',
                'UPDATE "sqlite_sequence" SET "seq" = 0 WHERE "name" IN '
                '(\'backends_person\', \'backends_tag\');',
            ],
        )

    def test_sql_flush_sequences_allow_cascade(self):
        """
        Flushes sequences for specified database tables with cascade option.
        
        This function generates SQL statements to delete data from specified
        database tables and reset their sequences. It takes into account the
        `allow_cascade` parameter to enable cascading deletes.
        
        Args:
        no_style (bool): Not used in this function.
        tables (list): List of table names to be flushed.
        reset_sequences (bool): If True, resets sequences after deleting data.
        allow_cascade (bool):
        """

        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
            reset_sequences=True,
            allow_cascade=True,
        )
        self.assertEqual(
            # The tables are processed in an unordered set.
            sorted(statements[:-1]),
            [
                'DELETE FROM "backends_person";',
                'DELETE FROM "backends_tag";',
                'DELETE FROM "backends_verylongmodelnamezzzzzzzzzzzzzzzzzzzzzz'
                'zzzzzzzzzzzzzzzzzzzz_m2m_also_quite_long_zzzzzzzzzzzzzzzzzzzz'
                'zzzzzzzzzzzzzzzzzzzzzzz";',
            ],
        )
        self.assertIs(statements[-1].startswith(
            'UPDATE "sqlite_sequence" SET "seq" = 0 WHERE "name" IN ('
        ), True)
        self.assertIn("'backends_person'", statements[-1])
        self.assertIn("'backends_tag'", statements[-1])
        self.assertIn(
            "'backends_verylongmodelnamezzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            "zzzz_m2m_also_quite_long_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            "zzz'",
            statements[-1],
        )
