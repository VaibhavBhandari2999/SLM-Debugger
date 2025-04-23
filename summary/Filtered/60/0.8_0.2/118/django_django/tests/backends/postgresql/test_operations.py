import unittest

from django.core.management.color import no_style
from django.db import connection
from django.db.models.expressions import Col
from django.db.models.functions import Cast
from django.test import SimpleTestCase

from ..models import Author, Book, Person, Tag


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests.")
class PostgreSQLOperationsTests(SimpleTestCase):
    def test_sql_flush(self):
        """
        Tests the SQL flush operation for specified database tables.
        
        Args:
        no_style (bool): A boolean indicating whether to apply any style to the SQL commands.
        table_names (list): A list of table names to be flushed.
        
        Returns:
        list: A list of SQL commands to truncate the specified tables.
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
        """
        Test SQL flush sequences.
        
        This function generates SQL commands to flush and reset sequences for specified database tables.
        The function takes no arguments but uses the `connection.ops.sql_flush` method to generate the SQL.
        It specifies the tables to flush and the `reset_sequences` flag to ensure sequence values are reset.
        The expected output is a list containing a single SQL command that truncates the specified tables and resets their sequences.
        
        Parameters:
        - no_style (django.db.backends.utils.SQLCompiler): An instance of SQLCompiler
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

    def test_prepare_join_on_clause_same_type(self):
        author_table = Author._meta.db_table
        author_id_field = Author._meta.get_field("id")
        lhs_expr, rhs_expr = connection.ops.prepare_join_on_clause(
            author_table,
            author_id_field,
            author_table,
            author_id_field,
        )
        self.assertEqual(lhs_expr, Col(author_table, author_id_field))
        self.assertEqual(rhs_expr, Col(author_table, author_id_field))

    def test_prepare_join_on_clause_different_types(self):
        """
        Prepare the join on clause for a database query involving different field types.
        
        This function prepares the join on clause for a database query that involves joining two tables, `Author` and `Book`, based on their respective fields. The function takes into account the different field types and ensures that the join condition is correctly formed.
        
        Parameters:
        - author_table (str): The name of the `Author` table.
        - author_id_field (Field): The `id` field of the `Author` model.
        -
        """

        author_table = Author._meta.db_table
        author_id_field = Author._meta.get_field("id")
        book_table = Book._meta.db_table
        book_fk_field = Book._meta.get_field("author")
        lhs_expr, rhs_expr = connection.ops.prepare_join_on_clause(
            author_table,
            author_id_field,
            book_table,
            book_fk_field,
        )
        self.assertEqual(lhs_expr, Col(author_table, author_id_field))
        self.assertEqual(
            rhs_expr, Cast(Col(book_table, book_fk_field), author_id_field)
        )
