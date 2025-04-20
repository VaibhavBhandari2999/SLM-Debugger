from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = 'Prints the SQL statements for resetting sequences for the given app name(s).'

    output_transaction = True

    def add_arguments(self, parser):
        """
        The `add_arguments` method is a custom method that extends the functionality of a base class's `add_arguments` method. It accepts a `parser` object as an argument. The method first calls the `add_arguments` method of the superclass, then adds an additional argument to the parser.
        
        Key Parameters:
        - `parser`: The argument parser object to which the new argument will be added.
        
        Additional Argument:
        - `--database`: A command-line argument that allows specifying a database to print the SQL
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle_app_config(self, app_config, **options):
        """
        Reset sequences for all models in the given app_config.
        
        This function is responsible for generating SQL statements to reset the sequences of database primary keys for all models in the specified app_config. It takes an app_config object and additional keyword arguments. The app_config must have a non-null models_module attribute. The function uses the connection from the specified database to generate the necessary SQL statements. If no sequences are found, it prints a message to the stderr. The function returns a string containing the generated SQL statements.
        """

        if app_config.models_module is None:
            return
        connection = connections[options['database']]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options['verbosity'] >= 1:
            self.stderr.write('No sequences found.')
        return '\n'.join(statements)
