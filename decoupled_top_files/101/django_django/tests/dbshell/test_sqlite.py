from pathlib import Path

from django.db.backends.sqlite3.client import DatabaseClient
from django.test import SimpleTestCase


class SqliteDbshellCommandTestCase(SimpleTestCase):
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

    def test_path_name(self):
        """
        Tests the `settings_to_cmd_args_env` function with a path name setting.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `settings_to_cmd_args_env` function by passing a dictionary containing a 'NAME' key with a `Path` object as its value. It asserts that the function returns a tuple containing a list with the command `sqlite3` and the provided path, and `None` as the second element of the tuple.
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({"NAME": Path("test.db.sqlite3")}),
            (["sqlite3", Path("test.db.sqlite3")], None),
        )

    def test_parameters(self):
        """
        Tests the `settings_to_cmd_args_env` function with a dictionary of settings and a list of command-line arguments.
        
        Args:
        None
        
        Returns:
        A tuple containing the expected command-line arguments and environment variables.
        
        Summary:
        This function tests the `settings_to_cmd_args_env` function by providing a dictionary of settings and a list of command-line arguments. It checks if the function returns the expected command-line arguments and environment variables, which are `["sqlite3", "test.db
        """

        self.assertEqual(
            self.settings_to_cmd_args_env({"NAME": "test.db.sqlite3"}, ["-help"]),
            (["sqlite3", "test.db.sqlite3", "-help"], None),
        )
