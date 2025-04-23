import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import TransactionTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class OperationsTests(TransactionTestCase):
    available_apps = ['backends']

    def test_sequence_name_truncation(self):
        seq_name = connection.ops._get_no_autofield_sequence_name('schema_authorwithevenlongee869')
        self.assertEqual(seq_name, 'SCHEMA_AUTHORWITHEVENLOB0B8_SQ')

    def test_bulk_batch_size(self):
        # Oracle restricts the number of parameters in a query.
        objects = range(2**16)
        self.assertEqual(connection.ops.bulk_batch_size([], objects), len(objects))
        # Each field is a parameter for each object.
        self.assertEqual(
            connection.ops.bulk_batch_size(['id'], objects),
            connection.features.max_query_params,
        )
        self.assertEqual(
            connection.ops.bulk_batch_size(['id', 'other'], objects),
            connection.features.max_query_params // 2,
        )

    def test_sql_flush(self):
        """
        Tests the SQL flush operation for specific database tables.
        
        This function tests the SQL flush operation on the database, truncating the specified tables and handling constraints appropriately. The operation involves disabling constraints, truncating the tables, and then re-enabling the constraints.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the `connection.ops.sql_flush` method to generate SQL statements for flushing the specified tables.
        - The tables `Person` and `Tag` are targeted for the flush
        """

        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
        )
        # The tables and constraints are processed in an unordered set.
        self.assertEqual(
            statements[0],
            'ALTER TABLE "BACKENDS_TAG" DISABLE CONSTRAINT '
            '"BACKENDS__CONTENT_T_FD9D7A85_F" KEEP INDEX;',
        )
        self.assertEqual(
            sorted(statements[1:-1]),
            [
                'TRUNCATE TABLE "BACKENDS_PERSON";',
                'TRUNCATE TABLE "BACKENDS_TAG";',
            ],
        )
        self.assertEqual(
            statements[-1],
            'ALTER TABLE "BACKENDS_TAG" ENABLE CONSTRAINT '
            '"BACKENDS__CONTENT_T_FD9D7A85_F";',
        )

    def test_sql_flush_allow_cascade(self):
        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
            allow_cascade=True,
        )
        # The tables and constraints are processed in an unordered set.
        self.assertEqual(
            statements[0],
            'ALTER TABLE "BACKENDS_VERYLONGMODELNAME540F" DISABLE CONSTRAINT '
            '"BACKENDS__PERSON_ID_1DD5E829_F" KEEP INDEX;',
        )
        self.assertEqual(
            sorted(statements[1:-1]),
            [
                'TRUNCATE TABLE "BACKENDS_PERSON";',
                'TRUNCATE TABLE "BACKENDS_TAG";',
                'TRUNCATE TABLE "BACKENDS_VERYLONGMODELNAME540F";',
            ],
        )
        self.assertEqual(
            statements[-1],
            'ALTER TABLE "BACKENDS_VERYLONGMODELNAME540F" ENABLE CONSTRAINT '
            '"BACKENDS__PERSON_ID_1DD5E829_F";',
        )

    def test_sql_flush_sequences(self):
        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
            reset_sequences=True,
        )
        # The tables and constraints are processed in an unordered set.
        self.assertEqual(
            statements[0],
            'ALTER TABLE "BACKENDS_TAG" DISABLE CONSTRAINT '
            '"BACKENDS__CONTENT_T_FD9D7A85_F" KEEP INDEX;',
        )
        self.assertEqual(
            sorted(statements[1:3]),
            [
                'TRUNCATE TABLE "BACKENDS_PERSON";',
                'TRUNCATE TABLE "BACKENDS_TAG";',
            ],
        )
        self.assertEqual(
            statements[3],
            'ALTER TABLE "BACKENDS_TAG" ENABLE CONSTRAINT '
            '"BACKENDS__CONTENT_T_FD9D7A85_F";',
        )
        # Sequences.
        self.assertEqual(len(statements[4:]), 2)
        self.assertIn('BACKENDS_PERSON_SQ', statements[4])
        self.assertIn('BACKENDS_TAG_SQ', statements[5])

    def test_sql_flush_sequences_allow_cascade(self):
        """
        Tests the SQL flush operation with sequences and cascade option.
        
        This function tests the SQL flush operation on the database, specifically focusing on the `reset_sequences` and `allow_cascade` parameters. It flushes the specified tables, truncates them, and ensures that constraints are properly disabled and re-enabled. The function also checks that the sequence reset operations are performed correctly.
        
        Parameters:
        - None (The function uses internal Django connection and model objects)
        
        Returns:
        - None (The function asserts the correctness of the
        """

        statements = connection.ops.sql_flush(
            no_style(),
            [Person._meta.db_table, Tag._meta.db_table],
            reset_sequences=True,
            allow_cascade=True,
        )
        # The tables and constraints are processed in an unordered set.
        self.assertEqual(
            statements[0],
            'ALTER TABLE "BACKENDS_VERYLONGMODELNAME540F" DISABLE CONSTRAINT '
            '"BACKENDS__PERSON_ID_1DD5E829_F" KEEP INDEX;',
        )
        self.assertEqual(
            sorted(statements[1:4]),
            [
                'TRUNCATE TABLE "BACKENDS_PERSON";',
                'TRUNCATE TABLE "BACKENDS_TAG";',
                'TRUNCATE TABLE "BACKENDS_VERYLONGMODELNAME540F";',
            ],
        )
        self.assertEqual(
            statements[4],
            'ALTER TABLE "BACKENDS_VERYLONGMODELNAME540F" ENABLE CONSTRAINT '
            '"BACKENDS__PERSON_ID_1DD5E829_F";',
        )
        # Sequences.
        self.assertEqual(len(statements[5:]), 3)
        self.assertIn('BACKENDS_PERSON_SQ', statements[5])
        self.assertIn('BACKENDS_VERYLONGMODELN7BE2_SQ', statements[6])
        self.assertIn('BACKENDS_TAG_SQ', statements[7])
