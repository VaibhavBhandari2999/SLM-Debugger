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
        Asserts that the provided constraint details match the expected values.
        
        Args:
        constraint_details (dict): The constraint details to be checked.
        cols (list): The columns associated with the constraint.
        unique (bool, optional): Indicates if the constraint is unique. Defaults to False.
        check (bool, optional): Indicates if the constraint is a check constraint. Defaults to False.
        
        Raises:
        AssertionError: If the provided constraint details do not match the expected values.
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
        Tests the parsing of unique column constraints in SQL definitions.
        
        This function tests the parsing of unique column constraints in SQL definitions. It takes a list of test cases, where each test case is a tuple containing a SQL definition string and a list of column names. The function iterates over these test cases, parsing each SQL definition and checking the results.
        
        Parameters:
        tests (tuple): A tuple of test cases, where each test case is a tuple containing a SQL definition string and a list of column names
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
        """
        Tests the parsing and validation of SQL check constraints.
        
        This function tests the parsing and validation of SQL check constraints. It takes a series of test cases, each consisting of an SQL constraint definition string, the expected constraint name, and a list of column names. For each test case, it parses the SQL string and checks if the extracted constraint name, details, and check expression match the expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Test Cases:
        1. 'CONSTRAINT "ref"
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
        Tests the parsing and validation of column constraints with operators and functions.
        
        This function tests the parsing and validation of column constraints that include operators and functions. It checks if the parsed elements match the expected results.
        
        Parameters:
        None
        
        Returns:
        None
        
        Test Cases:
        1. Tests a constraint with a simple integer range check.
        2. Tests a constraint with a LIKE operator check.
        3. Tests a constraint with a LENGTH function check.
        
        Each test case is defined in the `tests` tuple, where
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
check=True)
