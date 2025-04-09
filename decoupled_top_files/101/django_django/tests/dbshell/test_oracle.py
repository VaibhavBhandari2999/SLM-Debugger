from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.oracle.client import DatabaseClient
from django.test import SimpleTestCase


@skipUnless(connection.vendor == "oracle", "Requires cx_Oracle to be installed")
class OracleDbshellTests(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None, rlwrap=False):
        """
        Generate command-line arguments and environment variables based on database settings.
        
        Args:
        settings_dict (dict): A dictionary containing database settings.
        parameters (list, optional): Additional command-line parameters. Defaults to an empty list.
        rlwrap (bool, optional): Whether to use rlwrap for command-line editing. Defaults to False.
        
        Returns:
        tuple: A tuple containing the command-line arguments and environment variables.
        
        Summary:
        This function takes a dictionary of database settings and generates command-line
        """

        if parameters is None:
            parameters = []
        with mock.patch(
            "shutil.which", return_value="/usr/bin/rlwrap" if rlwrap else None
        ):
            return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_without_rlwrap(self):
        """
        Tests the `settings_to_cmd_args_env` function without using `rlwrap`.
        
        Args:
        None
        
        Returns:
        A tuple containing the expected command-line arguments and environment variables.
        
        Summary:
        This function tests the `settings_to_cmd_args_env` function with the `rlwrap` parameter set to `False`. It constructs the expected command-line arguments for the `sqlplus` command based on the provided database connection settings and asserts that the function returns the correct arguments and `None`
        """

        expected_args = [
            "sqlplus",
            "-L",
            connection.client.connect_string(connection.settings_dict),
        ]
        self.assertEqual(
            self.settings_to_cmd_args_env(connection.settings_dict, rlwrap=False),
            (expected_args, None),
        )

    def test_with_rlwrap(self):
        """
        Tests the generation of command-line arguments for connecting to a database using rlwrap.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `settings_to_cmd_args_env` method by comparing its output with an expected list of arguments. The method generates a list of command-line arguments for connecting to a database using rlwrap and sqlplus. The expected arguments include rlwrap, sqlplus, -L, and the client's connect string from the given database settings
        """

        expected_args = [
            "/usr/bin/rlwrap",
            "sqlplus",
            "-L",
            connection.client.connect_string(connection.settings_dict),
        ]
        self.assertEqual(
            self.settings_to_cmd_args_env(connection.settings_dict, rlwrap=True),
            (expected_args, None),
        )

    def test_parameters(self):
        """
        Tests the `settings_to_cmd_args_env` function with specific parameters.
        
        Args:
        connection: An object containing database connection settings.
        
        Returns:
        A tuple containing the expected command-line arguments and environment variables.
        
        Important Functions:
        - `settings_to_cmd_args_env`: The function being tested, which converts database connection settings into command-line arguments and environment variables.
        - `connection.client.connect_string`: Generates the client connect string from the connection settings.
        - `self.assertEqual`: Asserts
        """

        expected_args = [
            "sqlplus",
            "-L",
            connection.client.connect_string(connection.settings_dict),
            "-HELP",
        ]
        self.assertEqual(
            self.settings_to_cmd_args_env(
                connection.settings_dict,
                parameters=["-HELP"],
            ),
            (expected_args, None),
        )
