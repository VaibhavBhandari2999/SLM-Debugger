import sys

from psycopg2 import errorcodes

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.base.creation import BaseDatabaseCreation
from django.db.backends.utils import strip_quotes


class DatabaseCreation(BaseDatabaseCreation):

    def _quote_name(self, name):
        return self.connection.ops.quote_name(name)

    def _get_database_create_suffix(self, encoding=None, template=None):
        """
        Generate a suffix for a database creation command.
        
        This function constructs a suffix for a database creation command in SQL.
        The suffix can include an encoding and a template for the database.
        
        Parameters:
        encoding (str, optional): The character set encoding for the database.
        template (str, optional): The template database to base this database on.
        
        Returns:
        str: A string representing the suffix for the database creation command.
        
        Example:
        >>> _get_database_create_suffix(encoding='UTF8', template='
        """

        suffix = ""
        if encoding:
            suffix += " ENCODING '{}'".format(encoding)
        if template:
            suffix += " TEMPLATE {}".format(self._quote_name(template))
        return suffix and "WITH" + suffix

    def sql_table_creation_suffix(self):
        """
        Creates a suffix for PostgreSQL database table creation.
        
        This function generates a suffix for the SQL command used to create a PostgreSQL database. It checks if the 'COLLATION' setting is provided in the test settings and raises an ImproperlyConfigured exception if it is. If no 'COLLATION' is provided, it proceeds to generate the suffix using the specified encoding and template.
        
        Parameters:
        - self: The instance of the class containing the method.
        - encoding (str): The character set encoding
        """

        test_settings = self.connection.settings_dict['TEST']
        if test_settings.get('COLLATION') is not None:
            raise ImproperlyConfigured(
                'PostgreSQL does not support collation setting at database '
                'creation time.'
            )
        return self._get_database_create_suffix(
            encoding=test_settings['CHARSET'],
            template=test_settings.get('TEMPLATE'),
        )

    def _database_exists(self, cursor, database_name):
        cursor.execute('SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s', [strip_quotes(database_name)])
        return cursor.fetchone() is not None

    def _execute_create_test_db(self, cursor, parameters, keepdb=False):
        """
        Executes the creation of a test database.
        
        This method attempts to create a test database using the provided cursor and parameters. If the `keepdb` flag is set to `True` and the database already exists, it will not attempt to create a new one. If an exception occurs during the creation process, it will check if the error is due to a duplicate database. If the error is not related to a duplicate database, it will log the error and exit with a status code of 2
        """

        try:
            if keepdb and self._database_exists(cursor, parameters['dbname']):
                # If the database should be kept and it already exists, don't
                # try to create a new one.
                return
            super()._execute_create_test_db(cursor, parameters, keepdb)
        except Exception as e:
            if getattr(e.__cause__, 'pgcode', '') != errorcodes.DUPLICATE_DATABASE:
                # All errors except "database already exists" cancel tests.
                self.log('Got an error creating the test database: %s' % e)
                sys.exit(2)
            elif not keepdb:
                # If the database should be kept, ignore "database already
                # exists".
                raise

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        """
        Clones a test database with the specified suffix.
        
        This function creates a new database by cloning an existing one. It ensures that all connections to the template database are closed before proceeding. The function takes care of handling exceptions and ensures that the new database is properly created or destroyed if an error occurs.
        
        Parameters:
        suffix (str): A suffix to be appended to the test database name.
        verbosity (int): The level of detail to be printed during the process.
        keepdb (bool):
        """

        # CREATE DATABASE ... WITH TEMPLATE ... requires closing connections
        # to the template database.
        self.connection.close()

        source_database_name = self.connection.settings_dict['NAME']
        target_database_name = self.get_test_db_clone_settings(suffix)['NAME']
        test_db_params = {
            'dbname': self._quote_name(target_database_name),
            'suffix': self._get_database_create_suffix(template=source_database_name),
        }
        with self._nodb_cursor() as cursor:
            try:
                self._execute_create_test_db(cursor, test_db_params, keepdb)
            except Exception:
                try:
                    if verbosity >= 1:
                        self.log('Destroying old test database for alias %s...' % (
                            self._get_database_display_str(verbosity, target_database_name),
                        ))
                    cursor.execute('DROP DATABASE %(dbname)s' % test_db_params)
                    self._execute_create_test_db(cursor, test_db_params, keepdb)
                except Exception as e:
                    self.log('Got an error cloning the test database: %s' % e)
                    sys.exit(2)
