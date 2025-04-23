import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, connection
from django.db.backends.base.creation import BaseDatabaseCreation
from django.test import SimpleTestCase

try:
    from django.db.backends.postgresql.psycopg_any import errors
except ImportError:
    pass
else:
    from django.db.backends.postgresql.creation import DatabaseCreation


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests")
class DatabaseCreationTests(SimpleTestCase):
    @contextmanager
    def changed_test_settings(self, **kwargs):
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
        """
        Generate a Python docstring for the provided function.
        
        The function `check_sql_table_creation_suffix` is designed to test the suffix appended to SQL table creation statements. It takes a dictionary of settings and an expected suffix as input, temporarily modifies the database settings, and then checks if the generated suffix matches the expected one.
        
        Parameters:
        settings (dict): A dictionary containing the settings to be temporarily changed for the database connection.
        expected (str): The expected suffix that should be appended to the SQL table
        """

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
        Execute a database creation operation and raise a `DatabaseError` if the database already exists.
        
        This method attempts to create a database using the provided parameters. If the database already exists, it raises a `DatabaseError` with a specific error message indicating that the database already exists.
        
        Parameters:
        cursor (object): The database cursor used to execute the creation command.
        parameters (dict): A dictionary containing the parameters needed for the database creation, including the database name (`dbname`).
        keepdb (
        """

        error = errors.DuplicateDatabase(
            "database %s already exists" % parameters["dbname"]
        )
        raise DatabaseError() from error

    def _execute_raise_permission_denied(self, cursor, parameters, keepdb=False):
        error = errors.InsufficientPrivilege("permission denied to create database")
        raise DatabaseError() from error

    def patch_test_db_creation(self, execute_create_test_db):
        return mock.patch.object(
            BaseDatabaseCreation, "_execute_create_test_db", execute_create_test_db
        )

    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch("sys.stderr", new_callable=StringIO)
    def test_create_test_db(self, *mocked_objects):
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
