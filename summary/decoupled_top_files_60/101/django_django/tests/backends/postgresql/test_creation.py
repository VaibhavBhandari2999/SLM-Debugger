import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, connection
from django.db.backends.base.creation import BaseDatabaseCreation
from django.test import SimpleTestCase

try:
    import psycopg2  # NOQA
except ImportError:
    pass
else:
    from psycopg2 import errorcodes

    from django.db.backends.postgresql.creation import DatabaseCreation


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests")
class DatabaseCreationTests(SimpleTestCase):
    @contextmanager
    def changed_test_settings(self, **kwargs):
        """
        Modifies the test settings for a database connection temporarily.
        
        This function allows you to change the settings of the test database connection for the duration of a test. It saves the original settings, applies the new settings, runs the test, and then restores the original settings.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments where the key is the setting name and the value is the new setting value.
        
        Returns:
        None: This function does not return any value. It is intended to be used as a context
        """

        settings = connection.settings_dict["TEST"]
        saved_values = {}
        for name in kwargs:
            if name in settings:
                saved_values[name] = settings[name]

        for name, value in kwargs.items():
            settings[name] = value
        try:
            yield
        finally:
            for name in kwargs:
                if name in saved_values:
                    settings[name] = saved_values[name]
                else:
                    del settings[name]

    def check_sql_table_creation_suffix(self, settings, expected):
        with self.changed_test_settings(**settings):
            creation = DatabaseCreation(connection)
            suffix = creation.sql_table_creation_suffix()
            self.assertEqual(suffix, expected)

    def test_sql_table_creation_suffix_with_none_settings(self):
        settings = {"CHARSET": None, "TEMPLATE": None}
        self.check_sql_table_creation_suffix(settings, "")

    def test_sql_table_creation_suffix_with_encoding(self):
        settings = {"CHARSET": "UTF8"}
        self.check_sql_table_creation_suffix(settings, "WITH ENCODING 'UTF8'")

    def test_sql_table_creation_suffix_with_template(self):
        settings = {"TEMPLATE": "template0"}
        self.check_sql_table_creation_suffix(settings, 'WITH TEMPLATE "template0"')

    def test_sql_table_creation_suffix_with_encoding_and_template(self):
        """
        Test the SQL table creation suffix with specified encoding and template settings.
        
        This function checks the SQL table creation suffix to ensure it correctly includes the provided encoding and template settings.
        
        Parameters:
        settings (dict): A dictionary containing the settings for the table creation. Expected keys are 'CHARSET' and 'TEMPLATE'.
        
        Returns:
        str: The expected SQL suffix with the encoding and template settings applied.
        
        Example:
        >>> settings = {"CHARSET": "UTF8", "TEMPLATE": "template0"}
        """

        settings = {"CHARSET": "UTF8", "TEMPLATE": "template0"}
        self.check_sql_table_creation_suffix(
            settings, '''WITH ENCODING 'UTF8' TEMPLATE "template0"'''
        )

    def test_sql_table_creation_raises_with_collation(self):
        settings = {"COLLATION": "test"}
        msg = (
            "PostgreSQL does not support collation setting at database "
            "creation time."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.check_sql_table_creation_suffix(settings, None)

    def _execute_raise_database_already_exists(self, cursor, parameters, keepdb=False):
        """
        Execute a database operation that raises an error if the specified database already exists.
        
        This method is used to check if a database with the given name already exists in the database system. If the database exists, a `DatabaseError` is raised with a specific error code and message.
        
        Parameters:
        cursor (psycopg2.extensions.cursor): The database cursor used to execute the SQL command.
        parameters (dict): A dictionary containing the parameters for the SQL command, including the database name (`dbname`).
        
        Keywords
        """

        error = DatabaseError("database %s already exists" % parameters["dbname"])
        error.pgcode = errorcodes.DUPLICATE_DATABASE
        raise DatabaseError() from error

    def _execute_raise_permission_denied(self, cursor, parameters, keepdb=False):
        error = DatabaseError("permission denied to create database")
        error.pgcode = errorcodes.INSUFFICIENT_PRIVILEGE
        raise DatabaseError() from error

    def patch_test_db_creation(self, execute_create_test_db):
        return mock.patch.object(
            BaseDatabaseCreation, "_execute_create_test_db", execute_create_test_db
        )

    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch("sys.stderr", new_callable=StringIO)
    def test_create_test_db(self, *mocked_objects):
        """
        Creates and manages a test database for testing purposes.
        
        This function simulates the creation of a test database and handles various scenarios, including:
        
        - Simulating a "database already exists" error and prompting the user to either delete the database or continue.
        - Handling unexpected errors, such as "insufficient privileges", and ensuring that the function behaves correctly when the database already exists.
        - Using a mock object to simulate the execution of database creation commands.
        
        Parameters:
        *mocked_objects: Variable number of mocked
        """

        creation = DatabaseCreation(connection)
        # Simulate test database creation raising "database already exists"
        with self.patch_test_db_creation(self._execute_raise_database_already_exists):
            with mock.patch("builtins.input", return_value="no"):
                with self.assertRaises(SystemExit):
                    # SystemExit is raised if the user answers "no" to the
                    # prompt asking if it's okay to delete the test database.
                    creation._create_test_db(
                        verbosity=0, autoclobber=False, keepdb=False
                    )
            # "Database already exists" error is ignored when keepdb is on
            creation._create_test_db(verbosity=0, autoclobber=False, keepdb=True)
        # Simulate test database creation raising unexpected error
        with self.patch_test_db_creation(self._execute_raise_permission_denied):
            with mock.patch.object(
                DatabaseCreation, "_database_exists", return_value=False
            ):
                with self.assertRaises(SystemExit):
                    creation._create_test_db(
                        verbosity=0, autoclobber=False, keepdb=False
                    )
                with self.assertRaises(SystemExit):
                    creation._create_test_db(
                        verbosity=0, autoclobber=False, keepdb=True
                    )
        # Simulate test database creation raising "insufficient privileges".
        # An error shouldn't appear when keepdb is on and the database already
        # exists.
        with self.patch_test_db_creation(self._execute_raise_permission_denied):
            with mock.patch.object(
                DatabaseCreation, "_database_exists", return_value=True
            ):
                creation._create_test_db(verbosity=0, autoclobber=False, keepdb=True)
