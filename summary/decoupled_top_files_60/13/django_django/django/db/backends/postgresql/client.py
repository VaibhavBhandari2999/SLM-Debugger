import os
import signal
import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'psql'

    @classmethod
    def runshell_db(cls, conn_params):
        """
        Runs a shell command using the specified database connection parameters.
        
        This function constructs and executes a shell command to run a database client (psql by default) with the provided connection parameters. It handles optional parameters for user, host, port, and password, and ensures that the original signal handler for SIGINT is restored after the command execution.
        
        Parameters:
        cls (type): The class object that contains the `executable_name` attribute, which specifies the database client executable to use (default is 'psql
        """

        args = [cls.executable_name]

        host = conn_params.get('host', '')
        port = conn_params.get('port', '')
        dbname = conn_params.get('database', '')
        user = conn_params.get('user', '')
        passwd = conn_params.get('password', '')

        if user:
            args += ['-U', user]
        if host:
            args += ['-h', host]
        if port:
            args += ['-p', str(port)]
        args += [dbname]

        sigint_handler = signal.getsignal(signal.SIGINT)
        subprocess_env = os.environ.copy()
        if passwd:
            subprocess_env['PGPASSWORD'] = str(passwd)
        try:
            # Allow SIGINT to pass to psql to abort queries.
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            subprocess.run(args, check=True, env=subprocess_env)
        finally:
            # Restore the original SIGINT handler.
            signal.signal(signal.SIGINT, sigint_handler)

    def runshell(self):
        DatabaseClient.runshell_db(self.connection.get_connection_params())
