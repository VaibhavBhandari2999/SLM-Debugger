import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import SimpleTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests.")
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Test SQL flush.
        
        Args:
        no_style (callable): A function that returns a connection-specific SQL style.
        app_labels (list): A list of application labels to flush.
        
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
        Test the SQL flush operation with cascade option.
        
        This function checks the SQL command generated for flushing specified database tables with cascade option. The function takes no direct input but uses internal models `Person` and `Tag`. It asserts that the generated SQL command matches the expected output.
        
        Key Parameters:
        - `no_style()`: A method that returns a style class without any formatting.
        - `Person._meta.db_table`: The database table name for the `Person` model.
        - `Tag._meta.db_table
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
        Test SQL flush sequences.
        
        Args:
        no_style (callable): A callable that returns a string representation of the model's database table without any style.
        app_label (str): The name of the application containing the models to be flushed.
        reset_sequences (bool): If True, reset the sequences after truncating the tables.
        
        Returns:
        list: A list of SQL statements to flush and reset sequences for the specified tables.
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
        self.assertEqual(
            connection.ops.sql_flush(
                no_style(),
                [Person._meta.db_table, Tag._meta.db_table],
                reset_sequences=True,
                allow_cascade=True,
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY CASCADE;'],
        )
            ),
            ['TRUNCATE "backends_person", "backends_tag" RESTART IDENTITY CASCADE;'],
        )
