import unittest

from django.core.management.color import no_style
from django.db import connection
from django.test import SimpleTestCase

from ..models import Person, Tag


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests.")
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Test the SQL flush operation.
        
        This function checks the SQL command generated for flushing specific tables in a database. The `connection.ops.sql_flush` method is used to generate the SQL command. The method takes two parameters: a style object (which is not used in this case) and a list of table names to be flushed. The expected output is a list containing a single SQL command that truncates the specified tables.
        
        Parameters:
        - no_style: A style object that is not utilized in this function.
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
        
        This function checks the SQL command generated for flushing specified database tables with cascade option.
        
        Parameters:
        - no_style (BaseDatabaseOperations.no_style): A method that returns a no style object for the database operations.
        - table_list (list): A list of table names to be flushed, specified as database table names (e.g., 'backends_person', 'backends_tag').
        - allow_cascade (bool): A flag indicating whether to allow cascade operations during
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
        
        This function checks the SQL command generated for flushing sequences of specified database tables.
        
        Parameters:
        - no_style (BaseDatabaseOperations.no_style): A no_style function from the database operations.
        - tables (list): A list of table names to flush, in this case, 'Person._meta.db_table' and 'Tag._meta.db_table'.
        - reset_sequences (bool): A boolean indicating whether to reset sequences after flushing the tables.
        
        Returns:
        - list: A list
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
        Tests the SQL flush operation with sequences reset and cascade enabled.
        
        Args:
        no_style (callable): A function that returns SQL statements without any style applied.
        models (list): A list of model names (as strings) for which the flush operation is performed.
        reset_sequences (bool): If True, sequences for the tables will be reset after the flush operation.
        allow_cascade (bool): If True, cascading deletes will be allowed during the flush operation.
        
        Returns:
        list:
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
