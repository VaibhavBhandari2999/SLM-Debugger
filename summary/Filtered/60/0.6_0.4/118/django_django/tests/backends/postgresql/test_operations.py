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
        Tests the SQL flush operation for specific database tables.
        
        Args:
        no_style (callable): A function that returns a style object for database operations.
        app_labels (list): A list of application labels (table names) to flush.
        
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
        Prepare the join on clause for a database query.
        
        This function prepares the join on clause for a database query when joining two tables with different field types.
        
        Parameters:
        author_table (str): The name of the 'Author' table.
        author_id_field (Field): The 'id' field of the 'Author' model.
        book_table (str): The name of the 'Book' table.
        book_fk_field (Field): The foreign key field of the 'Book' model that references
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
