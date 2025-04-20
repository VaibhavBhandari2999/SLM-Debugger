from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.oracle.client import DatabaseClient
from django.test import SimpleTestCase


@skipUnless(connection.vendor == "oracle", "Requires cx_Oracle to be installed")
class OracleDbshellTests(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None, rlwrap=False):
        """
        Generate command-line arguments and environment variables for a database client based on given settings.
        
        This function takes a dictionary of database settings and a list of additional parameters, and returns a tuple containing the command-line arguments and environment variables. It can optionally enable rlwrap for command-line interaction.
        
        Parameters:
        settings_dict (dict): A dictionary containing database settings.
        parameters (list, optional): Additional command-line parameters to be included. Defaults to an empty list.
        rlwrap (bool, optional): Whether to
        """

        if parameters is None:
            parameters = []
        with mock.patch(
            "shutil.which", return_value="/usr/bin/rlwrap" if rlwrap else None
        ):
            return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_without_rlwrap(self):
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
        Tests the function `settings_to_cmd_args_env` for creating command-line arguments for SQLPlus based on provided database connection settings and optional parameters.
        
        Parameters:
        connection (object): An object containing database connection settings, including the client's connect string.
        settings_dict (dict): A dictionary of database connection settings.
        
        Returns:
        tuple: A tuple containing the expected command-line arguments and environment variables. The first element is a list of command-line arguments, and the second element is `None` (indic
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
