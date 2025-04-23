import shutil

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'sqlplus'
    wrapper_name = 'rlwrap'

    @staticmethod
    def connect_string(settings_dict):
        """
        Connects to a database using Oracle backend.
        
        This function constructs a connection string for a database using the Oracle backend. The connection string is formatted as a string with the username, password, and a DSN (Data Source Name) derived from the provided settings dictionary.
        
        Parameters:
        settings_dict (dict): A dictionary containing the database settings. It must include the following keys:
        - 'USER': The username for the database connection.
        - 'PASSWORD': The password for the database connection.
        """

        from django.db.backends.oracle.utils import dsn

        return '%s/"%s"@%s' % (
            settings_dict['USER'],
            settings_dict['PASSWORD'],
            dsn(settings_dict),
        )

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        args = [cls.executable_name, '-L', cls.connect_string(settings_dict)]
        wrapper_path = shutil.which(cls.wrapper_name)
        if wrapper_path:
            args = [wrapper_path, *args]
        args.extend(parameters)
        return args, None
 = [wrapper_path, *args]
        args.extend(parameters)
        return args, None
