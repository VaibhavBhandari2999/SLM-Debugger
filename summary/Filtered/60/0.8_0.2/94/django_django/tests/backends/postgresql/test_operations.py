import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import SimpleTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests.")
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Tests the SQL flush operation for specified database tables.
        
        Args:
        no_style (callable): A function that returns a SQL style object.
        app_labels (list): A list of application labels (e.g., ['backends']) to specify which tables to flush.
        
        Returns:
        list: A list of SQL statements to flush the specified tables.
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
            ),
            ['TRUNCATE "backends_person", "backends_tag";'],
        )

    def test_sql_flush_allow_cascade(self):
        """
        Test the SQL flush command with cascade option.
        
        Args:
        no_style (bool): A boolean indicating whether to use style formatting.
        app_labels (list): A list of application labels (e.g., ['backends']) for which to generate the SQL flush command.
        allow_cascade (bool): A boolean indicating whether to allow cascade operations during the flush.
        
        Returns:
        list: A list containing the SQL command as a string. In this case, it will be ['TRUNCATE "
        """

        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                allow_cascade=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" CASCADE;'],
        )

    def test_sql_flush_sequences(self):
        """
        Tests the SQL flush sequences functionality.
        
        This function generates SQL commands to flush sequences for specified database tables.
        The function takes no arguments but uses the `connection.ops.sql_flush` method to generate the SQL command.
        The `no_style()` method is used to ensure that the SQL command does not include any style formatting.
        The function expects two model classes, `Person` and `Tag`, to be provided as arguments to `sql_flush`.
        The `reset_sequences` parameter is set to `True` to ensure
        """

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
        
        This function tests the SQL flush operation that truncates specified tables and resets their sequences. It allows cascading operations.
        
        Parameters:
        no_style (bool): Whether to apply any database-specific styles.
        tables (list): List of table names to be truncated.
        reset_sequences (bool): Whether to reset sequences after truncation.
        allow_cascade (bool): Whether to allow cascading operations during truncation.
        
        Returns:
        list: A list containing the SQL
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
