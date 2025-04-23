import shutil

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = "sqlplus"
    wrapper_name = "rlwrap"

    @staticmethod
    def connect_string(settings_dict):
        """
        Generates a connection string for an Oracle database.
        
        This function constructs a connection string for an Oracle database using the provided settings dictionary. The connection string is formatted as 'USER/PASSWORD@DSN', where DSN is derived from the settings dictionary.
        
        Parameters:
        settings_dict (dict): A dictionary containing the following keys:
        - "USER" (str): The username for the database connection.
        - "PASSWORD" (str): The password for the database connection.
        - Other keys required
        """

        from django.db.backends.oracle.utils import dsn

        return '%s/"%s"@%s' % (
            settings_dict["USER"],
            settings_dict["PASSWORD"],
            dsn(settings_dict),
        )

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        args = [cls.executable_name, "-L", cls.connect_string(settings_dict)]
        wrapper_path = shutil.which(cls.wrapper_name)
        if wrapper_path:
            args = [wrapper_path, *args]
        args.extend(parameters)
        return args, None
