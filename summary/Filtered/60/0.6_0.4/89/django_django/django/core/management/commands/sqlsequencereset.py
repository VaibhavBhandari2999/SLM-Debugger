from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = 'Prints the SQL statements for resetting sequences for the given app name(s).'

    output_transaction = True

    def add_arguments(self, parser):
        """
        Adds custom arguments to the argument parser.
        
        This function extends the functionality of the base class by adding a custom argument '--database'. This argument allows the user to specify which database to print the SQL for. If no database is specified, it defaults to the 'default' database.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the custom argument will be added.
        
        Returns:
        None: This function does not return any value. It modifies the provided argument parser in place.
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            return
        connection = connections[options['database']]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options['verbosity'] >= 1:
            self.stderr.write('No sequences found.')
        return '\n'.join(statements)
 '\n'.join(statements)
