import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'sqlite3'

    def runshell(self):
        """
        Runs a shell command using the specified executable and database name.
        
        Args:
        self: The instance of the class containing the executable name and connection settings.
        
        Returns:
        None
        
        Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.
        
        Key Parameters:
        - executable_name (str): The name of the executable to run.
        - connection.settings_dict['NAME'] (str): The name of the database to pass to the executable.
        
        This function executes a shell command
        """

        args = [self.executable_name,
                self.connection.settings_dict['NAME']]
        subprocess.run(args, check=True)
