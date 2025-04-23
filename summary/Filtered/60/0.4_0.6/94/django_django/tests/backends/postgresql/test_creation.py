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
        
        This function allows you to change the settings for the test database connection
        during the execution of a block of code. The changes are automatically reverted
        after the block is executed.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments where the keys are the names of the
        settings to modify and the values are the new settings.
        
        Returns:
        None: The function does not return anything. It modifies the settings in place
        and reverts them
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
        """
        Generate a Python docstring for the provided function.
        
        The function `check_sql_table_creation_suffix` is designed to test the SQL table creation suffix for a given database connection. It takes a dictionary of settings and an expected suffix as input and asserts that the suffix returned by the `sql_table_creation_suffix` method of the `DatabaseCreation` class matches the expected value.
        
        Parameters:
        settings (dict): A dictionary containing the settings for the database connection.
        expected (str): The expected suffix for the
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
        """
        Test that creating a PostgreSQL database with a collation setting raises an ImproperlyConfigured exception.
        
        This function checks if an ImproperlyConfigured exception is raised when attempting to create a PostgreSQL database with a collation setting. The collation setting is specified in the settings dictionary under the key 'COLLATION'. If the settings include a collation, the function will raise an ImproperlyConfigured exception with a specific message indicating that PostgreSQL does not support collation settings at database creation time
        """

        settings = {"COLLATION": "test"}
        msg = (
            "PostgreSQL does not support collation setting at database "
            "creation time."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.check_sql_table_creation_suffix(settings, None)

    def _execute_raise_database_already_exists(self, cursor, parameters, keepdb=False):
        error = DatabaseError("database %s already exists" % parameters["dbname"])
        error.pgcode = errorcodes.DUPLICATE_DATABASE
        raise DatabaseError() from error

    def _execute_raise_permission_denied(self, cursor, parameters, keepdb=False):
        """
        Raise a permission denied error when attempting to create a database.
        
        This function is intended to be used internally to handle permission issues
        when creating a database. It raises a `DatabaseError` with a specific error
        code indicating insufficient privilege.
        
        Parameters:
        cursor (object): The database cursor object used for executing queries.
        parameters (tuple): Parameters passed to the query.
        keepdb (bool, optional): A flag indicating whether to keep the database
        after the operation. Defaults to False.
        """

        error = DatabaseError("permission denied to create database")
        error.pgcode = errorcodes.INSUFFICIENT_PRIVILEGE
        raise DatabaseError() from error

    def patch_test_db_creation(self, execute_create_test_db):
        """
        Patches the `_execute_create_test_db` method of the `BaseDatabaseCreation` class.
        
        This function is used to mock the creation of a test database during testing.
        
        Parameters:
        - execute_create_test_db (callable): A callable object that will be used to replace the original `_execute_create_test_db` method.
        
        Returns:
        - mock.patch: A mock patch object that can be used to temporarily replace the original method with the provided callable during testing.
        """

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
