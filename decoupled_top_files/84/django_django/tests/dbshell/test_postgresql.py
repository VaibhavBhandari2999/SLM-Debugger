"""
This Python file contains unit tests for the `settings_to_cmd_args_env` method of the `DatabaseClient` class in Django's PostgreSQL backend. The tests cover various scenarios such as basic database connection settings, SSL certificate configurations, service names, passfiles, and handling of special characters in usernames and passwords. Additionally, there are tests to ensure that the password does not leak in exceptions and that SIGINT is properly handled during shell execution. The tests use mocking and subprocess calls to simulate different conditions and validate the behavior of the `settings_to_cmd_args_env` method under these conditions. ```python
"""
import os
import signal
import subprocess
import sys
from pathlib import Path
from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.postgresql.client import DatabaseClient
from django.test import SimpleTestCase


class PostgreSqlDbshellCommandTestCase(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None):
        """
        Converts a dictionary of database settings to command-line arguments and environment variables.
        
        Args:
        settings_dict (dict): A dictionary containing database settings.
        parameters (list, optional): Additional parameters to be included in the command-line arguments. Defaults to an empty list.
        
        Returns:
        tuple: A tuple containing the command-line arguments and environment variables.
        
        Notes:
        This function utilizes the `settings_to_cmd_args_env` method from the `DatabaseClient` class to perform the conversion.
        """

        if parameters is None:
            parameters = []
        return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_basic(self):
        """
        Test the `settings_to_cmd_args_env` function.
        
        This function converts database settings into command-line arguments and environment variables for `psql`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output of `settings_to_cmd_args_env` does not match the expected result.
        
        Example:
        >>> self.settings_to_cmd_args_env({
        ...     'NAME': 'dbname',
        ...     'USER': 'someuser',
        ...     '
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': 'someuser',
                'PASSWORD': 'somepassword',
                'HOST': 'somehost',
                'PORT': '444',
            }), (
                ['psql', '-U', 'someuser', '-h', 'somehost', '-p', '444', 'dbname'],
                {'PGPASSWORD': 'somepassword'},
            )
        )

    def test_nopass(self):
        """
        Test the `settings_to_cmd_args_env` function with a database connection configuration that does not include a password.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the generated command arguments do not match the expected output.
        
        Important Functions:
        - settings_to_cmd_args_env: Converts database connection settings to command-line arguments.
        - assertEqual: Compares the generated command arguments with the expected output.
        
        Input Variables:
        - A dictionary containing the following
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': 'someuser',
                'HOST': 'somehost',
                'PORT': '444',
            }), (
                ['psql', '-U', 'someuser', '-h', 'somehost', '-p', '444', 'dbname'],
                None,
            )
        )

    def test_ssl_certificate(self):
        """
        Test SSL certificate configuration.
        
        This function verifies that the settings for SSL certificate, including
        `sslmode`, `sslrootcert`, `sslcert`, and `sslkey`, are correctly
        translated into command-line arguments and environment variables when
        using the `settings_to_cmd_args_env` function.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the expected command-line arguments and
        environment variables for the `psql` command with SSL
        configuration
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': 'someuser',
                'HOST': 'somehost',
                'PORT': '444',
                'OPTIONS': {
                    'sslmode': 'verify-ca',
                    'sslrootcert': 'root.crt',
                    'sslcert': 'client.crt',
                    'sslkey': 'client.key',
                },
            }), (
                ['psql', '-U', 'someuser', '-h', 'somehost', '-p', '444', 'dbname'],
                {
                    'PGSSLCERT': 'client.crt',
                    'PGSSLKEY': 'client.key',
                    'PGSSLMODE': 'verify-ca',
                    'PGSSLROOTCERT': 'root.crt',
                },
            )
        )

    def test_service(self):
        """
        Test the service configuration.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the command list and environment dictionary.
        
        Raises:
        None
        
        Important Functions:
        - `settings_to_cmd_args_env`: Converts settings to command arguments and environment variables.
        
        Input Variables:
        - `{'OPTIONS': {'service': 'django_test'}}`: A dictionary containing the service name.
        
        Output Variables:
        - `(['psql'], {'PGSERVICE': 'django_test'})`:
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({'OPTIONS': {'service': 'django_test'}}),
            (['psql'], {'PGSERVICE': 'django_test'}),
        )

    def test_passfile(self):
        """
        Test the `settings_to_cmd_args_env` function.
        
        This function tests the `settings_to_cmd_args_env` method, which converts database settings into command-line arguments and environment variables for the `psql` command. The test cases verify that the correct command-line arguments and environment variables are generated based on the provided database settings.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the generated command-line arguments or environment variables do not match the expected values.
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': 'someuser',
                'HOST': 'somehost',
                'PORT': '444',
                'OPTIONS': {
                    'passfile': '~/.custompgpass',
                },
            }),
            (
                ['psql', '-U', 'someuser', '-h', 'somehost', '-p', '444', 'dbname'],
                {'PGPASSFILE': '~/.custompgpass'},
            ),
        )
        self.assertEqual(
            self.settings_to_cmd_args_env({
                'OPTIONS': {
                    'service': 'django_test',
                    'passfile': '~/.custompgpass',
                },
            }),
            (
                ['psql'], {'PGSERVICE': 'django_test', 'PGPASSFILE': '~/.custompgpass'},
            ),
        )

    def test_column(self):
        """
        Test the conversion of database settings to command-line arguments and environment variables.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the expected command-line arguments list and environment variables dictionary.
        
        Raises:
        AssertionError: If the generated command-line arguments or environment variables do not match the expected values.
        
        Example:
        >>> test_column()
        (['psql', '-U', 'some:user', '-h', '::1', '-p', '444', 'dbname'],
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': 'some:user',
                'PASSWORD': 'some:password',
                'HOST': '::1',
                'PORT': '444',
            }), (
                ['psql', '-U', 'some:user', '-h', '::1', '-p', '444', 'dbname'],
                {'PGPASSWORD': 'some:password'},
            )
        )

    def test_accent(self):
        """
        Test the `settings_to_cmd_args_env` function with a username containing an accent ('rôle') and a password ('sésame'). The function should return a tuple containing a list of command-line arguments and a dictionary of environment variables.
        
        Args:
        None (The test case is self-contained within the function body).
        
        Returns:
        A tuple:
        - First element: A list of command-line arguments for the `psql` command.
        - Second element: A dictionary of
        """

        username = 'rôle'
        password = 'sésame'
        self.assertEqual(
            self.settings_to_cmd_args_env({
                'NAME': 'dbname',
                'USER': username,
                'PASSWORD': password,
                'HOST': 'somehost',
                'PORT': '444',
            }), (
                ['psql', '-U', username, '-h', 'somehost', '-p', '444', 'dbname'],
                {'PGPASSWORD': password},
            )
        )

    def test_parameters(self):
        """
        Tests the `settings_to_cmd_args_env` function with a dictionary of settings and a list of command-line arguments, expecting a tuple containing the constructed command and environment variables.
        
        Args:
        self: The instance of the class containing the `settings_to_cmd_args_env` method.
        
        Returns:
        A tuple containing the expected command and environment variables.
        
        Example:
        >>> self.settings_to_cmd_args_env({'NAME': 'dbname'}, ['--help'])
        (['psql', 'dbname',
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({'NAME': 'dbname'}, ['--help']),
            (['psql', 'dbname', '--help'], None),
        )

    @skipUnless(connection.vendor == 'postgresql', 'Requires a PostgreSQL connection')
    def test_sigint_handler(self):
        """SIGINT is ignored in Python and passed to psql to abort queries."""
        def _mock_subprocess_run(*args, **kwargs):
            handler = signal.getsignal(signal.SIGINT)
            self.assertEqual(handler, signal.SIG_IGN)

        sigint_handler = signal.getsignal(signal.SIGINT)
        # The default handler isn't SIG_IGN.
        self.assertNotEqual(sigint_handler, signal.SIG_IGN)
        with mock.patch('subprocess.run', new=_mock_subprocess_run):
            connection.client.runshell([])
        # dbshell restores the original handler.
        self.assertEqual(sigint_handler, signal.getsignal(signal.SIGINT))

    def test_crash_password_does_not_leak(self):
        """
        Tests that the password does not leak in an exception resulting from a client crash.
        
        Args:
        self: The instance of the class containing this method.
        
        Summary:
        This function tests whether the password is leaked in an exception caused by a client crash. It uses the `settings_to_cmd_args_env` function to set up environment variables, the `subprocess.run` function to execute a fake client script, and checks if the password is present in the exception message.
        
        Important Functions:
        """

        # The password doesn't leak in an exception that results from a client
        # crash.
        args, env = self.settings_to_cmd_args_env({'PASSWORD': 'somepassword'}, [])
        if env:
            env = {**os.environ, **env}
        fake_client = Path(__file__).with_name('fake_client.py')
        args[0:1] = [sys.executable, str(fake_client)]
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            subprocess.run(args, check=True, env=env)
        self.assertNotIn('somepassword', str(ctx.exception))
