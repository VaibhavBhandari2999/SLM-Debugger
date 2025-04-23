import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import SimpleTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests.")
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Test SQL flush for database tables.
        
        This function checks the SQL command generated for flushing specified database tables.
        The function takes no arguments but uses the `Person` and `Tag` models to determine the tables to flush.
        It returns a list containing the SQL command to truncate the specified tables.
        
        Parameters:
        - no_style (BaseDatabaseOperations.no_style): A method to get the SQL without any style applied.
        
        Returns:
        - list: A list containing the SQL command to truncate the specified tables.
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
        Test SQL flush with cascade.
        
        Args:
        no_style (bool): Whether to use style formatting for SQL commands.
        models (list): List of model names (table names) to be flushed.
        allow_cascade (bool): Whether to allow cascade operations during the flush.
        
        Returns:
        list: A list containing the SQL command to flush the specified models with cascade.
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
        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY;'],
        )

    def test_sql_flush_sequences_allow_cascade(self):
        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
                allow_cascade=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY CASCADE;'],
        )
