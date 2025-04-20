import os
import shutil
import sys

from django.db.backends.base.creation import BaseDatabaseCreation


class DatabaseCreation(BaseDatabaseCreation):

    @staticmethod
    def is_in_memory_db(database_name):
        return database_name == ':memory:' or 'mode=memory' in database_name

    def _get_test_db_name(self):
        """
        Generate a test database name for the current connection.
        
        This function returns the name of the test database to be used. If the test database name is set to ':memory:', it returns a modified string that specifies an in-memory database with shared caching. Otherwise, it returns the original test database name.
        
        Parameters:
        None
        
        Returns:
        str: The name of the test database to be used for testing.
        """

        test_database_name = self.connection.settings_dict['TEST']['NAME'] or ':memory:'
        if test_database_name == ':memory:':
            return 'file:memorydb_%s?mode=memory&cache=shared' % self.connection.alias
        return test_database_name

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        test_database_name = self._get_test_db_name()

        if keepdb:
            return test_database_name
        if not self.is_in_memory_db(test_database_name):
            # Erase the old test database
            if verbosity >= 1:
                self.log('Destroying old test database for alias %s...' % (
                    self._get_database_display_str(verbosity, test_database_name),
                ))
            if os.access(test_database_name, os.F_OK):
                if not autoclobber:
                    confirm = input(
                        "Type 'yes' if you would like to try deleting the test "
                        "database '%s', or 'no' to cancel: " % test_database_name
                    )
                if autoclobber or confirm == 'yes':
                    try:
                        os.remove(test_database_name)
                    except Exception as e:
                        self.log('Got an error deleting the old test database: %s' % e)
                        sys.exit(2)
                else:
                    self.log('Tests cancelled.')
                    sys.exit(1)
        return test_database_name

    def get_test_db_clone_settings(self, suffix):
        orig_settings_dict = self.connection.settings_dict
        source_database_name = orig_settings_dict['NAME']
        if self.is_in_memory_db(source_database_name):
            return orig_settings_dict
        else:
            root, ext = os.path.splitext(orig_settings_dict['NAME'])
            return {**orig_settings_dict, 'NAME': '{}_{}.{}'.format(root, suffix, ext)}

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        """
        Clones a test database for a given suffix.
        
        This function is used to create a copy of the test database for a specific suffix. It takes care of handling in-memory databases and ensures that the old test database is destroyed if it exists and `keepdb` is not set to True. The function also provides feedback based on the verbosity level.
        
        Parameters:
        suffix (str): The suffix to be used for the new test database name.
        verbosity (int): The level of detail to log.
        """

        source_database_name = self.connection.settings_dict['NAME']
        target_database_name = self.get_test_db_clone_settings(suffix)['NAME']
        # Forking automatically makes a copy of an in-memory database.
        if not self.is_in_memory_db(source_database_name):
            # Erase the old test database
            if os.access(target_database_name, os.F_OK):
                if keepdb:
                    return
                if verbosity >= 1:
                    self.log('Destroying old test database for alias %s...' % (
                        self._get_database_display_str(verbosity, target_database_name),
                    ))
                try:
                    os.remove(target_database_name)
                except Exception as e:
                    self.log('Got an error deleting the old test database: %s' % e)
                    sys.exit(2)
            try:
                shutil.copy(source_database_name, target_database_name)
            except Exception as e:
                self.log('Got an error cloning the test database: %s' % e)
                sys.exit(2)

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Destroys the test database.
        
        This function removes the SQLite database file specified by `test_database_name` if it is not an in-memory database.
        
        Parameters:
        test_database_name (str): The name of the test database to be destroyed.
        verbosity (int): The level of detail to output during the operation. Higher values indicate more detailed output.
        
        Returns:
        None: This function does not return any value. It only removes the specified database file.
        
        Note:
        This function should be used in
        """

        if test_database_name and not self.is_in_memory_db(test_database_name):
            # Remove the SQLite database file
            os.remove(test_database_name)

    def test_db_signature(self):
        """
        Return a tuple that uniquely identifies a test database.

        This takes into account the special cases of ":memory:" and "" for
        SQLite since the databases will be distinct despite having the same
        TEST NAME. See https://www.sqlite.org/inmemorydb.html
        """
        test_database_name = self._get_test_db_name()
        sig = [self.connection.settings_dict['NAME']]
        if self.is_in_memory_db(test_database_name):
            sig.append(self.connection.alias)
        return tuple(sig)
