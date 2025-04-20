from pathlib import Path

from django.db.backends.sqlite3.client import DatabaseClient
from django.test import SimpleTestCase


class SqliteDbshellCommandTestCase(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None):
        if parameters is None:
            parameters = []
        return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_path_name(self):
        self.assertEqual(
            self.settings_to_cmd_args_env({"NAME": Path("test.db.sqlite3")}),
            (["sqlite3", Path("test.db.sqlite3")], None),
        )

    def test_parameters(self):
        """
        Tests the `settings_to_cmd_args_env` function to ensure it correctly converts a dictionary of settings to command-line arguments and environment variables, and handles additional command-line parameters.
        
        Parameters:
        - settings (dict): A dictionary containing the settings to be converted to command-line arguments and environment variables.
        - extra_args (list): A list of additional command-line arguments to be appended to the generated command-line arguments.
        
        Returns:
        - tuple: A tuple containing the expected command-line arguments list and the expected environment variables dictionary
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({"NAME": "test.db.sqlite3"}, ["-help"]),
            (["sqlite3", "test.db.sqlite3", "-help"], None),
        )
