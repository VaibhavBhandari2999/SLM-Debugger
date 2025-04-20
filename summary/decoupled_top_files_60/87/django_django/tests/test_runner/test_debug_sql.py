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

    class ErrorSetUpTestDataTest(TestCase):
        @classmethod
        def setUpTestData(cls):
            raise Exception

        def runTest(self):
            pass

    class PassingSubTest(TestCase):
        def runTest(self):
            with self.subTest():
                Person.objects.filter(first_name='subtest-pass').count()

    class FailingSubTest(TestCase):
        def runTest(self):
            with self.subTest():
                Person.objects.filter(first_name='subtest-fail').count()
                self.fail()

    class ErrorSubTest(TestCase):
        def runTest(self):
            """
            Runs a test to check for a specific person in the database.
            
            This function uses a subtest to filter and count persons with the first name 'subtest-error'. If such a person is found, it raises an exception.
            
            Parameters:
            None
            
            Returns:
            None
            
            Raises:
            Exception: If a person with the first name 'subtest-error' is found in the database.
            
            Usage:
            This function is typically used within a testing framework to validate the presence or absence of specific records in
            """

            with self.subTest():
                Person.objects.filter(first_name='subtest-error').count()
                raise Exception

    def _test_output(self, verbosity):
        """
        Runs a test suite with specified verbosity and returns the test output.
        
        This function sets up a test suite with various test cases, runs the tests, and captures the output. It uses a custom test runner with debug SQL enabled.
        
        Parameters:
        verbosity (int): The verbosity level for the test runner. Determines the amount of detail in the test output.
        
        Returns:
        str: The captured test output as a string.
        
        Key Components:
        - `runner`: A `DiscoverRunner` instance configured with debug
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
        full_output = self._test_output(1)
        for output in self.expected_outputs:
            self.assertIn(output, full_output)
        for output in self.verbose_expected_outputs:
            self.assertNotIn(output, full_output)

    def test_output_verbose(self):
        """
        Tests the verbose output of a function.
        
        This function checks if the verbose output of a function matches the expected outputs. It runs the function with a verbosity level of 2 and verifies that all expected outputs and verbose expected outputs are present in the full output.
        
        Parameters:
        self: The instance of the class containing the expected outputs and verbose expected outputs.
        
        Returns:
        None: This function does not return any value. It only checks the outputs and raises an assertion error if the outputs do not match the
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

    def test_setupclass_exception(self):
        runner = DiscoverRunner(debug_sql=True, verbosity=0)
        suite = runner.test_suite()
        suite.addTest(self.ErrorSetUpTestDataTest())
        old_config = runner.setup_databases()
        stream = StringIO()
        runner.test_runner(
            verbosity=0,
            stream=stream,
            resultclass=runner.get_resultclass(),
        ).run(suite)
        runner.teardown_databases(old_config)
        output = stream.getvalue()
        self.assertIn(
            'ERROR: setUpClass '
            '(test_runner.test_debug_sql.TestDebugSQL.ErrorSetUpTestDataTest)',
            output,
        )
