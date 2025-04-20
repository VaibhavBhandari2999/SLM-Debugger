import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'sqlite3'

    def runshell(self):
        """
        Runs a shell command using the specified executable and database name.
        
        This function executes a shell command with the given executable and database name as arguments.
        
        Parameters:
        self (object): The instance of the class containing the executable name and connection settings.
        
        Returns:
        None: This function does not return any value. It executes a shell command using subprocess.check_call.
        
        Example:
        To run a shell command with an executable named 'my_executable' and a database name 'my_db', you would call:
        """

        args = [self.executable_name,
                self.connection.settings_dict['NAME']]
        subprocess.check_call(args)
