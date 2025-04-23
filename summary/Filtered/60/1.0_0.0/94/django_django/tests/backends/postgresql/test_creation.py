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
        during a test. The changes are applied temporarily and restored to their original
        values after the test completes.
        
        Parameters:
        **kwargs: A dictionary of settings to modify. The keys should match the
        settings in the test database configuration.
        
        Returns:
        None: The function does not return a value. It modifies the settings in place.
        
        Example:
        >>> changed_test_settings
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
        settings = {"CHARSET": "UTF8", "TEMPLATE": "template0"}
        self.check_sql_table_creation_suffix(
            settings, '''WITH ENCODING 'UTF8' TEMPLATE "template0"'''
        )

    def test_sql_table_creation_raises_with_collation(self):
        """
        Test that creating a PostgreSQL database with a collation setting raises an error.
        
        This function checks if setting a collation during database creation results in an `ImproperlyConfigured` exception being raised. The collation setting is specified in the `COLLATION` setting dictionary. If the function is successful, it means that the test has correctly identified that PostgreSQL does not support collation settings at the time of database creation.
        
        Parameters:
        settings (dict): A dictionary containing the database settings, including
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
        Execute a database operation that raises a permission denied error.
        
        This method is used to raise a `DatabaseError` with a specific error message and code when a user does not have sufficient privileges to create a database.
        
        Parameters:
        cursor (psycopg2.extensions.cursor): The database cursor object used to execute the operation.
        parameters (tuple): Parameters to be used in the database operation.
        keepdb (bool, optional): A flag indicating whether to keep the database after the operation. Defaults to False
        """

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
