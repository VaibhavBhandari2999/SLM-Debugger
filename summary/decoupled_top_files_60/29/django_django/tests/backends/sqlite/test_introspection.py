import unittest

import sqlparse

from django.db import connection
from django.test import TestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class IntrospectionTests(TestCase):
    def test_get_primary_key_column(self):
        """
        Get the primary key column regardless of whether or not it has
        quotation.
        """
        testable_column_strings = (
            ('id', 'id'), ('[id]', 'id'), ('`id`', 'id'), ('"id"', 'id'),
            ('[id col]', 'id col'), ('`id col`', 'id col'), ('"id col"', 'id col')
        )
        with connection.cursor() as cursor:
            for column, expected_string in testable_column_strings:
                sql = 'CREATE TABLE test_primary (%s int PRIMARY KEY NOT NULL)' % column
                with self.subTest(column=column):
                    try:
                        cursor.execute(sql)
                        field = connection.introspection.get_primary_key_column(cursor, 'test_primary')
                        self.assertEqual(field, expected_string)
                    finally:
                        cursor.execute('DROP TABLE test_primary')


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class ParsingTests(TestCase):
    def parse_definition(self, sql, columns):
        """Parse a column or constraint definition."""
        statement = sqlparse.parse(sql)[0]
        tokens = (token for token in statement.flatten() if not token.is_whitespace)
        with connection.cursor():
            return connection.introspection._parse_column_or_constraint_definition(tokens, set(columns))

    def assertConstraint(self, constraint_details, cols, unique=False, check=False):
        """
        Asserts that a given constraint details dictionary matches the expected values for a database constraint.
        
        Parameters:
        constraint_details (dict): The dictionary containing the constraint details to be checked.
        cols (list): The list of columns that the constraint applies to.
        unique (bool, optional): Indicates if the constraint is a unique constraint. Defaults to False.
        check (bool, optional): Indicates if the constraint is a check constraint. Defaults to False.
        
        This function checks if the provided `constraint_details`
        """

        self.assertEqual(constraint_details, {
            'unique': unique,
            'columns': cols,
            'primary_key': False,
            'foreign_key': None,
            'check': check,
            'index': False,
        })

    def test_unique_column(self):
        tests = (
            ('"ref" integer UNIQUE,', ['ref']),
            ('ref integer UNIQUE,', ['ref']),
            ('"customname" integer UNIQUE,', ['customname']),
            ('customname integer UNIQUE,', ['customname']),
        )
        for sql, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertIsNone(constraint)
                self.assertConstraint(details, columns, unique=True)
                self.assertIsNone(check)

    def test_unique_constraint(self):
        tests = (
            ('CONSTRAINT "ref" UNIQUE ("ref"),', 'ref', ['ref']),
            ('CONSTRAINT ref UNIQUE (ref),', 'ref', ['ref']),
            ('CONSTRAINT "customname1" UNIQUE ("customname2"),', 'customname1', ['customname2']),
            ('CONSTRAINT customname1 UNIQUE (customname2),', 'customname1', ['customname2']),
        )
        for sql, constraint_name, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertEqual(constraint, constraint_name)
                self.assertConstraint(details, columns, unique=True)
                self.assertIsNone(check)

    def test_unique_constraint_multicolumn(self):
        """
        Tests the parsing and extraction of unique constraints from SQL statements.
        
        This function tests the parsing of unique constraints defined in SQL statements. It processes a series of test cases where each test case consists of a SQL statement defining a unique constraint, the expected constraint name, and the expected columns involved in the unique constraint.
        
        Parameters:
        - sql (str): The SQL statement defining the unique constraint.
        - constraint_name (str): The expected name of the unique constraint.
        - columns (list): The expected columns involved in
        """

        tests = (
            ('CONSTRAINT "ref" UNIQUE ("ref", "customname"),', 'ref', ['ref', 'customname']),
            ('CONSTRAINT ref UNIQUE (ref, customname),', 'ref', ['ref', 'customname']),
        )
        for sql, constraint_name, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertEqual(constraint, constraint_name)
                self.assertConstraint(details, columns, unique=True)
                self.assertIsNone(check)

    def test_check_column(self):
        tests = (
            ('"ref" varchar(255) CHECK ("ref" != \'test\'),', ['ref']),
            ('ref varchar(255) CHECK (ref != \'test\'),', ['ref']),
            ('"customname1" varchar(255) CHECK ("customname2" != \'test\'),', ['customname2']),
            ('customname1 varchar(255) CHECK (customname2 != \'test\'),', ['customname2']),
        )
        for sql, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertIsNone(constraint)
                self.assertIsNone(details)
                self.assertConstraint(check, columns, check=True)

    def test_check_constraint(self):
        tests = (
            ('CONSTRAINT "ref" CHECK ("ref" != \'test\'),', 'ref', ['ref']),
            ('CONSTRAINT ref CHECK (ref != \'test\'),', 'ref', ['ref']),
            ('CONSTRAINT "customname1" CHECK ("customname2" != \'test\'),', 'customname1', ['customname2']),
            ('CONSTRAINT customname1 CHECK (customname2 != \'test\'),', 'customname1', ['customname2']),
        )
        for sql, constraint_name, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertEqual(constraint, constraint_name)
                self.assertIsNone(details)
                self.assertConstraint(check, columns, check=True)

    def test_check_column_with_operators_and_functions(self):
        tests = (
            ('"ref" integer CHECK ("ref" BETWEEN 1 AND 10),', ['ref']),
            ('"ref" varchar(255) CHECK ("ref" LIKE \'test%\'),', ['ref']),
            ('"ref" varchar(255) CHECK (LENGTH(ref) > "max_length"),', ['ref', 'max_length']),
        )
        for sql, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertIsNone(constraint)
                self.assertIsNone(details)
                self.assertConstraint(check, columns, check=True)

    def test_check_and_unique_column(self):
        """
        Tests the `test_check_and_unique_column` function to ensure it correctly parses SQL column definitions with unique and check constraints.
        
        Parameters:
        - sql (str): The SQL column definition string to be parsed.
        - columns (list): A list of column names expected to be extracted from the SQL string.
        
        Returns:
        - None: The function asserts the correctness of the parsing through internal checks.
        
        Test Cases:
        1. Parses a column definition with a unique constraint and a check constraint.
        2. Parses a column definition
        """

        tests = (
            ('"ref" varchar(255) CHECK ("ref" != \'test\') UNIQUE,', ['ref']),
            ('ref varchar(255) UNIQUE CHECK (ref != \'test\'),', ['ref']),
        )
        for sql, columns in tests:
            with self.subTest(sql=sql):
                constraint, details, check, _ = self.parse_definition(sql, columns)
                self.assertIsNone(constraint)
                self.assertConstraint(details, columns, unique=True)
                self.assertConstraint(check, columns, check=True)
