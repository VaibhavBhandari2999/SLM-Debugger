"""
This Python file contains unit tests for debugging SQL queries in a Django application. It defines several test cases to verify different scenarios involving filtering and counting `Person` objects based on their `first_name`. The tests are designed to cover passing, failing, and error conditions, both at the top-level test case and within sub-tests.

The file includes a custom test runner (`TestDebugSQL`) that runs these tests and captures the SQL queries executed during the test process. The captured SQL queries are then compared against expected outputs to ensure they match the intended behavior.

Key functionalities and interactions:
- **Test Cases**: Defines various test cases (`PassingTest`, `FailingTest`, `ErrorTest`, etc.) to test different conditions.
- **Sub-Tests
"""
import unittest
from io import StringIO

from django.db import connection
from django.test import TestCase
from django.test.runner import DiscoverRunner

from .models import Person


@unittest.skipUnless(connection.vendor == 'sqlite', 'Only run on sqlite so we can check output SQL.')
class TestDebugSQL(unittest.TestCase):

    class PassingTest(TestCase):
        def runTest(self):
            Person.objects.filter(first_name='pass').count()

    class FailingTest(TestCase):
        def runTest(self):
            Person.objects.filter(first_name='fail').count()
            self.fail()

    class ErrorTest(TestCase):
        def runTest(self):
            Person.objects.filter(first_name='error').count()
            raise Exception

    class PassingSubTest(TestCase):
        def runTest(self):
            with self.subTest():
                Person.objects.filter(first_name='subtest-pass').count()

    class FailingSubTest(TestCase):
        def runTest(self):
            """
            Runs a test case for filtering and counting persons with a specific first name ('subtest-fail') using Django's ORM. The test fails intentionally after the count operation.
            
            Summary:
            - Uses `self.subTest()` to create a sub-test context.
            - Filters `Person` objects where `first_name` is 'subtest-fail' using `filter()`.
            - Counts the filtered objects using `count()`.
            - Calls `self.fail()` to intentionally fail the test.
            """

            with self.subTest():
                Person.objects.filter(first_name='subtest-fail').count()
                self.fail()

    class ErrorSubTest(TestCase):
        def runTest(self):
            """
            Runs a test case for filtering and counting persons with the first name 'subtest-error' in the database. Raises an exception if any such person is found.
            
            This function uses a subtest context manager to isolate the test case. It filters the `Person` objects where the `first_name` field is 'subtest-error' and counts them. If the count is greater than zero, an exception is raised.
            """

            with self.subTest():
                Person.objects.filter(first_name='subtest-error').count()
                raise Exception

    def _test_output(self, verbosity):
        """
        Runs a test suite with specified verbosity level and returns the test output.
        
        Args:
        verbosity (int): The verbosity level of the test output.
        
        Returns:
        str: The test output as a string.
        """

        runner = DiscoverRunner(debug_sql=True, verbosity=0)
        suite = runner.test_suite()
        suite.addTest(self.FailingTest())
        suite.addTest(self.ErrorTest())
        suite.addTest(self.PassingTest())
        suite.addTest(self.PassingSubTest())
        suite.addTest(self.FailingSubTest())
        suite.addTest(self.ErrorSubTest())
        old_config = runner.setup_databases()
        stream = StringIO()
        resultclass = runner.get_resultclass()
        runner.test_runner(
            verbosity=verbosity,
            stream=stream,
            resultclass=resultclass,
        ).run(suite)
        runner.teardown_databases(old_config)

        return stream.getvalue()

    def test_output_normal(self):
        """
        Tests the output of a function with normal parameters.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the output of another function using the `_test_output` method with an input parameter of 1. It checks if each expected output is present in the full output and ensures that no verbose expected outputs are included. The important functions used are `_test_output` and `assertIn`/`assertNotIn`.
        """

        full_output = self._test_output(1)
        for output in self.expected_outputs:
            self.assertIn(output, full_output)
        for output in self.verbose_expected_outputs:
            self.assertNotIn(output, full_output)

    def test_output_verbose(self):
        """
        Tests the verbose output of a function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the verbose output of a function by comparing the expected outputs and verbose expected outputs with the actual output generated by calling the `_test_output` function with an argument of 2. The `expected_outputs` and `verbose_expected_outputs` lists are used to check if the actual output contains all the expected and verbose expected outputs. The `_test_output` function is called to
        """

        full_output = self._test_output(2)
        for output in self.expected_outputs:
            self.assertIn(output, full_output)
        for output in self.verbose_expected_outputs:
            self.assertIn(output, full_output)

    expected_outputs = [
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'error';'''),
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'fail';'''),
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'subtest-error';'''),
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'subtest-fail';'''),
    ]

    verbose_expected_outputs = [
        'runTest (test_runner.test_debug_sql.TestDebugSQL.FailingTest) ... FAIL',
        'runTest (test_runner.test_debug_sql.TestDebugSQL.ErrorTest) ... ERROR',
        'runTest (test_runner.test_debug_sql.TestDebugSQL.PassingTest) ... ok',
        # If there are errors/failures in subtests but not in test itself,
        # the status is not written. That behavior comes from Python.
        'runTest (test_runner.test_debug_sql.TestDebugSQL.FailingSubTest) ...',
        'runTest (test_runner.test_debug_sql.TestDebugSQL.ErrorSubTest) ...',
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'pass';'''),
        ('''SELECT COUNT(*) AS "__count" '''
            '''FROM "test_runner_person" WHERE '''
            '''"test_runner_person"."first_name" = 'subtest-pass';'''),
    ]
