import os
import signal
import subprocess
import sys
from pathlib import Path
from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.mysql.client import DatabaseClient
from django.test import SimpleTestCase


class MySqlDbshellCommandTestCase(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None):
        """
        Generate command-line arguments and environment variables from a dictionary of database settings.
        
        This function converts a dictionary of database settings into command-line arguments and environment variables. It is typically used for initializing a database client with specific settings.
        
        Parameters:
        settings_dict (dict): A dictionary containing database settings such as host, port, user, password, and database name.
        parameters (list, optional): Additional parameters to be included in the command-line arguments. Defaults to an empty list.
        
        Returns:
        tuple: A
        """

        if parameters is None:
            parameters = []
        return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_fails_with_keyerror_on_incomplete_config(self):
        with self.assertRaises(KeyError):
            self.settings_to_cmd_args_env({})

    def test_basic_params_specified_in_settings(self):
        expected_args = [
            "mysql",
            "--user=someuser",
            "--host=somehost",
            "--port=444",
            "somedbname",
        ]
        expected_env = {"MYSQL_PWD": "somepassword"}
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "somedbname",
                    "USER": "someuser",
                    "PASSWORD": "somepassword",
                    "HOST": "somehost",
                    "PORT": 444,
                    "OPTIONS": {},
                }
            ),
            (expected_args, expected_env),
        )

    def test_options_override_settings_proper_values(self):
        """
        Function to test if options override settings with proper values.
        
        This function checks if the provided options correctly override the settings for database connection parameters. It ensures that the expected arguments and environment variables are generated as per the provided options.
        
        Parameters:
        - settings_port (int): The port number from the settings.
        - options_port (int): The port number from the options.
        
        Returns:
        - None: This function does not return any value. It uses assertions to validate the behavior.
        
        Key Assertions:
        1. The settings
        """

        settings_port = 444
        options_port = 555
        self.assertNotEqual(settings_port, options_port, "test pre-req")
        expected_args = [
            "mysql",
            "--user=optionuser",
            "--host=optionhost",
            "--port=%s" % options_port,
            "optiondbname",
        ]
        expected_env = {"MYSQL_PWD": "optionpassword"}
        for keys in [("database", "password"), ("db", "passwd")]:
            with self.subTest(keys=keys):
                database, password = keys
                self.assertEqual(
                    self.settings_to_cmd_args_env(
                        {
                            "NAME": "settingdbname",
                            "USER": "settinguser",
                            "PASSWORD": "settingpassword",
                            "HOST": "settinghost",
                            "PORT": settings_port,
                            "OPTIONS": {
                                database: "optiondbname",
                                "user": "optionuser",
                                password: "optionpassword",
                                "host": "optionhost",
                                "port": options_port,
                            },
                        }
                    ),
                    (expected_args, expected_env),
                )

    def test_options_non_deprecated_keys_preferred(self):
        """
        Tests the function `settings_to_cmd_args_env` to ensure that it correctly handles non-deprecated keys in the settings dictionary and prefers them over deprecated keys. The function should construct the command arguments and environment variables based on the provided settings.
        
        Parameters:
        - settings (dict): A dictionary containing database settings, including both non-deprecated and deprecated keys.
        
        Returns:
        - tuple: A tuple containing two elements:
        1. A list of command arguments (expected_args).
        2. A dictionary of
        """

        expected_args = [
            "mysql",
            "--user=someuser",
            "--host=somehost",
            "--port=444",
            "optiondbname",
        ]
        expected_env = {"MYSQL_PWD": "optionpassword"}
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "settingdbname",
                    "USER": "someuser",
                    "PASSWORD": "settingpassword",
                    "HOST": "somehost",
                    "PORT": 444,
                    "OPTIONS": {
                        "database": "optiondbname",
                        "db": "deprecatedoptiondbname",
                        "password": "optionpassword",
                        "passwd": "deprecatedoptionpassword",
                    },
                }
            ),
            (expected_args, expected_env),
        )

    def test_options_charset(self):
        expected_args = [
            "mysql",
            "--user=someuser",
            "--host=somehost",
            "--port=444",
            "--default-character-set=utf8",
            "somedbname",
        ]
        expected_env = {"MYSQL_PWD": "somepassword"}
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "somedbname",
                    "USER": "someuser",
                    "PASSWORD": "somepassword",
                    "HOST": "somehost",
                    "PORT": 444,
                    "OPTIONS": {"charset": "utf8"},
                }
            ),
            (expected_args, expected_env),
        )

    def test_can_connect_using_sockets(self):
        """
        Tests the ability to connect to a MySQL database using sockets.
        
        This function checks if the correct command-line arguments and environment variables are generated for connecting to a MySQL database using a socket file. The expected arguments include the MySQL command, user, socket file path, and the database name. The expected environment variable includes the password.
        
        Parameters:
        - None (The function uses predefined expected arguments and environment variables).
        
        Returns:
        - tuple: A tuple containing the expected command-line arguments and environment variables.
        
        Example:
        >>> expected
        """

        expected_args = [
            "mysql",
            "--user=someuser",
            "--socket=/path/to/mysql.socket.file",
            "somedbname",
        ]
        expected_env = {"MYSQL_PWD": "somepassword"}
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "somedbname",
                    "USER": "someuser",
                    "PASSWORD": "somepassword",
                    "HOST": "/path/to/mysql.socket.file",
                    "PORT": None,
                    "OPTIONS": {},
                }
            ),
            (expected_args, expected_env),
        )

    def test_ssl_certificate_is_added(self):
        expected_args = [
            "mysql",
            "--user=someuser",
            "--host=somehost",
            "--port=444",
            "--ssl-ca=sslca",
            "--ssl-cert=sslcert",
            "--ssl-key=sslkey",
            "somedbname",
        ]
        expected_env = {"MYSQL_PWD": "somepassword"}
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "somedbname",
                    "USER": "someuser",
                    "PASSWORD": "somepassword",
                    "HOST": "somehost",
                    "PORT": 444,
                    "OPTIONS": {
                        "ssl": {
                            "ca": "sslca",
                            "cert": "sslcert",
                            "key": "sslkey",
                        },
                    },
                }
            ),
            (expected_args, expected_env),
        )

    def test_parameters(self):
        self.assertEqual(
            self.settings_to_cmd_args_env(
                {
                    "NAME": "somedbname",
                    "USER": None,
                    "PASSWORD": None,
                    "HOST": None,
                    "PORT": None,
                    "OPTIONS": {},
                },
                ["--help"],
            ),
            (["mysql", "somedbname", "--help"], None),
        )

    def test_crash_password_does_not_leak(self):
        """
        Tests that the password does not leak in an exception resulting from a client crash.
        
        This function ensures that when a client crashes, the password used for database connection does not appear in the exception message. The function takes care of setting up the necessary environment and command-line arguments to simulate a client crash scenario.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Prepare the command-line arguments and environment variables for the database client.
        2. Replace the actual client executable with a fake client script
        """

        # The password doesn't leak in an exception that results from a client
        # crash.
        args, env = DatabaseClient.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": 444,
                "OPTIONS": {},
            },
            [],
        )
        if env:
            env = {**os.environ, **env}
        fake_client = Path(__file__).with_name("fake_client.py")
        args[0:1] = [sys.executable, str(fake_client)]
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            subprocess.run(args, check=True, env=env)
        self.assertNotIn("somepassword", str(ctx.exception))

    @skipUnless(connection.vendor == "mysql", "Requires a MySQL connection")
    def test_sigint_handler(self):
        """SIGINT is ignored in Python and passed to mysql to abort queries."""

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
