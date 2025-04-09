"""
This Python script is part of a Django project and is designed to facilitate the discovery and execution of tests within specified modules or the current directory. It leverages Django's built-in management command framework to provide a robust testing interface.

#### Classes Defined:
- **Command**: A subclass of `BaseCommand` from Django's `management.base` module. This class is responsible for handling the logic related to running tests, including parsing command-line arguments and executing the test suite using a configured test runner.

#### Functions Defined:
- **run_from_argv**: This method pre-parses the command-line arguments to extract the value of the `--testrunner` option, allowing for customization of the test runner.
- **add_arguments**: Configures the argument parser for
"""
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.utils import get_command_line_option
from django.test.utils import NullTimeKeeper, TimeKeeper, get_runner


class Command(BaseCommand):
    help = 'Discover and run tests in the specified modules or the current directory.'

    # DiscoverRunner runs the checks after databases are set up.
    requires_system_checks = []
    test_runner = None

    def run_from_argv(self, argv):
        """
        Pre-parse the command line to extract the value of the --testrunner
        option. This allows a test runner to define additional command line
        arguments.
        """
        self.test_runner = get_command_line_option(argv, '--testrunner')
        super().run_from_argv(argv)

    def add_arguments(self, parser):
        """
        This function configures and extends the argument parser for a testing command. It accepts several command-line arguments that control various aspects of the test execution process.
        
        **Parameters:**
        - `parser`: The argument parser instance to which the test-specific arguments will be added.
        
        **Arguments Added:**
        - `args`: Accepts zero or more module paths to test, which can be formatted as `modulename`, `modulename.TestCase`, or `modulename.TestCase.test_method`.
        """

        parser.add_argument(
            'args', metavar='test_label', nargs='*',
            help='Module paths to test; can be modulename, modulename.TestCase or modulename.TestCase.test_method'
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--failfast', action='store_true',
            help='Tells Django to stop running the test suite after first failed test.',
        )
        parser.add_argument(
            '--testrunner',
            help='Tells Django to use specified test runner class instead of '
                 'the one specified by the TEST_RUNNER setting.',
        )

        test_runner_class = get_runner(settings, self.test_runner)

        if hasattr(test_runner_class, 'add_arguments'):
            test_runner_class.add_arguments(parser)

    def handle(self, *test_labels, **options):
        """
        Runs tests specified by `test_labels` using the configured test runner.
        
        Args:
        *test_labels (str): Labels of the tests to be executed.
        **options (dict): Additional options for the test runner, including 'testrunner' and 'timing'.
        
        Returns:
        bool: True if all tests pass, False otherwise.
        
        Summary:
        This function uses the configured test runner to execute tests based on the provided labels. It measures the total execution time using `TimeKeeper`
        """

        TestRunner = get_runner(settings, options['testrunner'])

        time_keeper = TimeKeeper() if options.get('timing', False) else NullTimeKeeper()
        test_runner = TestRunner(**options)
        with time_keeper.timed('Total run'):
            failures = test_runner.run_tests(test_labels)
        time_keeper.print_results()
        if failures:
            sys.exit(1)
