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
        settings (dict): A dictionary containing the database settings with keys 'NAME', 'USER', 'PASSWORD', 'HOST', and 'PORT'.
        
        Returns:
        tuple: A tuple containing the command-line arguments list and the environment variables dictionary.
        """

        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": "someuser",
                    "PASSWORD": "somepassword",
                    "HOST": "somehost",
                    "PORT": "444",
                }
            ),
            (
                ["psql", "-U", "someuser", "-h", "somehost", "-p", "444", "dbname"],
                {"PGPASSWORD": "somepassword"},
            ),
        )

    def test_nopass(self):
        """
        Tests the `settings_to_cmd_args_env` function with a database connection configuration that does not include a password.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the expected command-line arguments list and environment variables.
        
        Expected Output:
        (["psql", "-U", "someuser", "-h", "somehost", "-p", "444", "dbname"], None)
        """

        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": "someuser",
                    "HOST": "somehost",
                    "PORT": "444",
                }
            ),
            (
                ["psql", "-U", "someuser", "-h", "somehost", "-p", "444", "dbname"],
                None,
            ),
        )

    def test_ssl_certificate(self):
        """
        Tests the SSL certificate configuration for a PostgreSQL connection.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the command arguments list and environment variables dictionary for configuring SSL certificate settings.
        
        Summary:
        This function tests the SSL certificate configuration by setting up the necessary command-line arguments and environment variables for a PostgreSQL connection using the `psql` command. The important functions used are `settings_to_cmd_args_env`, which converts the given settings into command-line arguments and environment variables, and the
        """

        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": "someuser",
                    "HOST": "somehost",
                    "PORT": "444",
                    "OPTIONS": {
                        "sslmode": "verify-ca",
                        "sslrootcert": "root.crt",
                        "sslcert": "client.crt",
                        "sslkey": "client.key",
                    },
                }
            ),
            (
                ["psql", "-U", "someuser", "-h", "somehost", "-p", "444", "dbname"],
                {
                    "PGSSLCERT": "client.crt",
                    "PGSSLKEY": "client.key",
                    "PGSSLMODE": "verify-ca",
                    "PGSSLROOTCERT": "root.crt",
                },
            ),
        )

    def test_service(self):
        """
        Tests the `settings_to_cmd_args_env` function with a specific service setting.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the command arguments list and environment variables dictionary.
        
        Summary:
        This function tests the `settings_to_cmd_args_env` function by passing a settings dictionary with the 'service' key set to 'django_test'. The expected output is a tuple with a list containing the command ['psql'] and a dictionary with the environment variable PGSERVICE set
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({"OPTIONS": {"service": "django_test"}}),
            (["psql"], {"PGSERVICE": "django_test"}),
        )

    def test_passfile(self):
        """
        Tests the `settings_to_cmd_args_env` function, which converts database settings into command-line arguments and environment variables.
        
        - **Input**: Database settings dictionary containing keys such as 'NAME', 'USER', 'HOST', 'PORT', and 'OPTIONS'.
        - **Output**: A tuple containing a list of command-line arguments and a dictionary of environment variables.
        
        Examples:
        - When 'OPTIONS' contains 'passfile', the function returns a list of arguments with the specified passfile and a
        """

        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": "someuser",
                    "HOST": "somehost",
                    "PORT": "444",
                    "OPTIONS": {
                        "passfile": "~/.custompgpass",
                    },
                }
            ),
            (
                ["psql", "-U", "someuser", "-h", "somehost", "-p", "444", "dbname"],
                {"PGPASSFILE": "~/.custompgpass"},
            ),
        )
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "OPTIONS": {
                        "service": "django_test",
                        "passfile": "~/.custompgpass",
                    },
                }
            ),
            (
                ["psql"],
                {"PGSERVICE": "django_test", "PGPASSFILE": "~/.custompgpass"},
            ),
        )

    def test_column(self):
        """
        Tests the `settings_to_cmd_args_env` function by verifying that it correctly converts database settings into command-line arguments and environment variables.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the function does not produce the expected command-line arguments and environment variables.
        
        Example:
        >>> test_column()
        (['psql', '-U', 'some:user', '-h', '::1', '-p', '444', 'dbname'], {'PGPASSWORD
        """

        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": "some:user",
                    "PASSWORD": "some:password",
                    "HOST": "::1",
                    "PORT": "444",
                }
            ),
            (
                ["psql", "-U", "some:user", "-h", "::1", "-p", "444", "dbname"],
                {"PGPASSWORD": "some:password"},
            ),
        )

    def test_accent(self):
        """
        Tests the conversion of database connection settings to command-line arguments and environment variables.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `settings_to_cmd_args_env` method by providing a username with an accent ("rôle") and a password ("sésame"). It verifies that the method correctly converts the provided settings into the expected command-line arguments and environment variables. The method is expected to return a tuple containing the command-line arguments list and a dictionary of
        """

        username = "rôle"
        password = "sésame"
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "dbname",
                    "USER": username,
                    "PASSWORD": password,
                    "HOST": "somehost",
                    "PORT": "444",
                }
            ),
            (
                ["psql", "-U", username, "-h", "somehost", "-p", "444", "dbname"],
                {"PGPASSWORD": password},
            ),
        )

    def test_parameters(self):
        """
        Tests the `settings_to_cmd_args_env` function with a dictionary of settings and a list of command-line arguments, expecting a tuple containing the constructed command and environment variables.
        
        Args:
        self: The instance of the class containing the `settings_to_cmd_args_env` method.
        
        Returns:
        A tuple containing the expected command and environment variables.
        
        Example:
        >>> self.settings_to_cmd_args_env({"NAME": "dbname"}, ["--help"])
        (["psql", "dbname",
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({"NAME": "dbname"}, ["--help"]),
            (["psql", "dbname", "--help"], None),
        )

    @skipUnless(connection.vendor == "postgresql", "Requires a PostgreSQL connection")
    def test_sigint_handler(self):
        """SIGINT is ignored in Python and passed to psql to abort queries."""

        def _mock_subprocess_run(*args, **kwargs):
            handler = signal.getsignal(signal.SIGINT)
            self.assertEqual(handler, signal.SIG_IGN)

        sigint_handler = signal.getsignal(signal.SIGINT)
        # The default handler isn't SIG_IGN.
        self.assertNotEqual(sigint_handler, signal.SIG_IGN)
        with mock.patch("subprocess.run", new=_mock_subprocess_run):
            connection.client.runshell([])
        # dbshell restores the original handler.
        self.assertEqual(sigint_handler, signal.getsignal(signal.SIGINT))

    def test_crash_password_does_not_leak(self):
        """
        Tests that the password does not leak in an exception resulting from a client crash.
        
        Args:
        self: The instance of the class containing this method.
        
        Summary:
        This function tests whether the password is leaked in an exception caused by a client crash. It uses the `settings_to_cmd_args_env` function to set the environment variables, and the `subprocess.run` function to run the client script. The `assertNotIn` function is used to ensure that the password is not present
        """

        # The password doesn't leak in an exception that results from a client
        # crash.
        args, env = self.settings_to_cmd_args_env({"PASSWORD": "somepassword"}, [])
        if env:
            env = {**os.environ, **env}
        fake_client = Path(__file__).with_name("fake_client.py")
        args[0:1] = [sys.executable, str(fake_client)]
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            subprocess.run(args, check=True, env=env)
        self.assertNotIn("somepassword", str(ctx.exception))
