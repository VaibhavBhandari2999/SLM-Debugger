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
        Asserts that the given constraint details match the expected values.
        
        Args:
        constraint_details (dict): The constraint details to be validated.
        cols (list): The columns associated with the constraint.
        unique (bool, optional): Indicates if the constraint is unique. Defaults to False.
        check (bool, optional): Indicates if the constraint is a check constraint. Defaults to False.
        
        Raises:
        AssertionError: If the constraint details do not match the expected values.
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
        """
        Tests the parsing of unique column constraints from SQL definitions.
        
        This function iterates over a series of test cases, each containing an SQL definition
        and a list of column names. It parses the SQL definition to extract the unique constraint,
        checks if the extracted details match the expected column names, and ensures that no
        additional check constraint is present.
        
        Args:
        None (The function uses predefined test cases within its body).
        
        Test Cases:
        - 'ref' integer UNIQUE,
        """

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
        """
        Tests the parsing of unique constraints from SQL definitions.
        
        This function iterates over a series of test cases, each containing an SQL
        definition of a unique constraint and the expected constraint name and
        column(s). It parses the SQL definition using the `parse_definition` method,
        extracts the constraint name and column(s), and verifies that the parsed
        constraint matches the expected values.
        
        Args:
        None
        
        Yields:
        None
        
        Keyword Args:
        None
        """

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
        Tests the parsing of unique constraints defined over multiple columns.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the parsing of unique constraints defined over multiple columns by extracting the constraint name and column names from the given SQL definition. It iterates through a series of test cases, each containing an SQL definition string, a constraint name, and a list of column names. For each test case, it parses the SQL definition using the `parse_definition` method and checks
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
        """
        Tests the parsing of column constraints from SQL definitions.
        
        This function iterates over a series of test cases, each containing an SQL definition string and a list of expected column names. It parses the SQL definition to extract the column name(s) associated with the CHECK constraint. The function ensures that no constraint is found, no additional details are returned, and the parsed check constraint matches the expected columns.
        
        Args:
        None
        
        Returns:
        None
        
        Test Cases:
        - 'ref'
        """

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
        """
        Tests the parsing and validation of SQL check constraints.
        
        This function iterates over a series of test cases, each containing an SQL
        constraint definition string, the expected constraint name, and the columns
        involved in the constraint. For each test case, it parses the SQL string,
        extracts the constraint name, and validates the columns involved in the
        constraint. The function uses the `parse_definition` method to parse the
        SQL string and the `assertConstraint` method to validate
        """

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
        """
        Tests the parsing of column constraints with operators and functions.
        
        This function iterates over a series of test cases, each containing an SQL
        constraint definition and a list of expected column names. For each test case,
        it parses the SQL definition, extracts the constraint, and checks if the parsed
        columns match the expected ones.
        
        Args:
        None
        
        Yields:
        None
        
        Raises:
        AssertionError: If the parsed columns do not match the expected ones or
        """

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
        Tests the parsing of SQL column definitions with unique and check constraints.
        
        This function iterates over a series of test cases, each containing an SQL definition string and a list of expected column names. For each test case, it parses the SQL definition to extract the unique and check constraints, and verifies that the parsed details match the expected results.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `parse_definition`: Parses the SQL definition string to extract constraints and details
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
