import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import TestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class SQLiteOperationsTests(TestCase):
    def test_sql_flush(self):
        """
        Test the SQL flush operation for database tables.
        
        This function checks the SQL commands generated for flushing specified tables
        from the database. The `connection.ops.sql_flush` method is used to generate
        the SQL commands. The method takes a style object (obtained using `no_style()`)
        and a list of table names to be flushed.
        
        Parameters:
        no_style (callable): A callable that returns a style object used for
        formatting SQL commands.
        
        Returns:
        list: A list of SQL
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
        Tests the behavior of the `sql_flush` function with `reset_sequences=True` and `allow_cascade=True`.
        
        This function executes a series of SQL statements to flush the specified database tables, allowing cascading deletes and resetting sequences. The function then verifies the generated SQL statements to ensure they match the expected output.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The function uses `connection.ops.sql_flush` to generate SQL statements for flushing the `Person` and `Tag` tables
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
     )
