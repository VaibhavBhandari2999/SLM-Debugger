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

    def test_fails_with_keyerror_on_incomplete_config(self):
        with self.assertRaises(KeyError):
            self.settings_to_cmd_args_env({})

    def test_basic_params_specified_in_settings(self):
        """
        Tests the generation of command-line arguments and environment variables based on database settings.
        
        Summary:
        - Input: Database settings including name, user, password, host, port, and options.
        - Output: Expected command-line arguments and environment variables.
        - Functions Used: `settings_to_cmd_args_env`
        - Important Variables: `expected_args`, `expected_env`
        
        Args:
        - settings (dict): A dictionary containing database settings.
        
        Returns:
        - tuple: A tuple containing
        """

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
        Tests that options override settings with proper values.
        
        This function verifies that when specific options are provided in the settings, they correctly override the corresponding settings values. It uses the `settings_port` and `options_port` to ensure they are different, then constructs expected command-line arguments (`expected_args`) and environment variables (`expected_env`). The function iterates over a list of key pairs, where each pair represents a setting and its corresponding option. For each pair, it calls `settings_to_cmd_args_env
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
        Tests that non-deprecated keys in the OPTIONS dictionary are preferred over deprecated keys when constructing command-line arguments and environment variables.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `self.settings_to_cmd_args_env`: Converts database settings to command-line arguments and environment variables.
        - `self.assertEqual`: Compares the expected command-line arguments and environment variables with the actual ones generated by the function under test.
        
        Expected Input:
        - A dictionary containing database settings,
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
        """
        Tests the generation of command-line arguments and environment variables for a MySQL database connection.
        
        This function verifies that the `settings_to_cmd_args_env` method correctly converts the provided database settings into the expected command-line arguments and environment variables. The important components include:
        - `mysql`: The command being executed.
        - `--user`, `--host`, `--port`, `--default-character-set`: Command-line options for specifying the database user, host, port, and character set.
        -
        """

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
        Tests the connection using sockets.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the connection to a MySQL database using sockets. It constructs the expected command arguments and environment variables based on the provided settings and compares them with the actual arguments and environment variables generated by the `settings_to_cmd_args_env` method. The important keywords and functions used are: `mysql`, `--user`, `--socket`, `somedbname`, `self.settings_to_cmd
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
        """
        Tests that SSL certificate options are correctly added to the command arguments and environment variables.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `self.settings_to_cmd_args_env`: Converts database settings to command arguments and environment variables.
        - `self.assertEqual`: Compares the generated command arguments and environment variables with the expected values.
        
        Expected Input Variables:
        - `expected_args`: List of command arguments including SSL certificate options.
        - `expected_env`: Dictionary of
        """

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
        """
        Tests the `settings_to_cmd_args_env` method with specific database settings and command-line arguments.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the expected command-line arguments list and environment variables.
        
        Raises:
        AssertionError: If the output of `settings_to_cmd_args_env` does not match the expected result.
        
        Example:
        >>> test_parameters()
        (['mysql', 'somedbname', '--help'], None)
        """

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
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        subprocess.CalledProcessError: If the subprocess call fails.
        
        Important Functions:
        - `DatabaseClient.settings_to_cmd_args_env`: Converts database settings to command-line arguments and environment variables.
        - `subprocess.run`: Executes the command with specified arguments and environment variables.
        - `assertNotIn`: Verifies that the password is
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
