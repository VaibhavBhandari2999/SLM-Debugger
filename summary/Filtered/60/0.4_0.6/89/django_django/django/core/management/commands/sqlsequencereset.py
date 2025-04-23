from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = 'Prints the SQL statements for resetting sequences for the given app name(s).'

    output_transaction = True

    def add_arguments(self, parser):
        """
        This function adds command-line arguments to an argument parser for a Django management command.
        
        Parameters:
        - parser (argparse.ArgumentParser): The argument parser to which the new argument will be added.
        
        Key Parameters:
        - `--database` (str): Specifies the database to print the SQL for. The default value is 'default'.
        
        Returns:
        None: This function does not return any value. It modifies the provided argument parser in place.
        
        Summary:
        The function extends the argument parser with a new argument that allows specifying
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle_app_config(self, app_config, **options):
        """
        Reset sequences for all models in the given app_config.
        
        This function processes the models in the specified app_config and generates SQL statements to reset the sequences for those models. It takes an app_config object and additional options as input. The app_config should contain a models_module, and the function uses the connection from the specified database to generate the sequence reset SQL. If no sequences are found, a message is printed to the stderr. The function returns a string containing the generated SQL statements.
        
        Parameters:
        app
        """

        if app_config.models_module is None:
            return
        connection = connections[options['database']]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options['verbosity'] >= 1:
            self.stderr.write('No sequences found.')
        return '\n'.join(statements)
