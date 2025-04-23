from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = 'Prints the SQL statements for resetting sequences for the given app name(s).'

    output_transaction = True

    def add_arguments(self, parser):
        """
        The `add_arguments` method is a custom method that extends the functionality of a base class's `add_arguments` method. It adds a new argument to the argument parser.
        
        Key Parameters:
        - `self`: The instance of the class.
        - `parser`: The argument parser to which the new argument will be added.
        
        Additional Argument:
        - `--database`: A command-line argument that allows the user to specify which database to print the SQL for. The default value is `DEFAULT_DB_ALIAS`.
        
        Returns
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle_app_config(self, app_config, **options):
        """
        Reset sequences for all models in the given app configuration.
        
        This function is responsible for generating SQL statements to reset the sequences for all models in the specified app configuration. It takes an `app_config` object which contains the models module, and optional keyword arguments `**options`. The `options` can include a 'database' key to specify which database connection to use.
        
        Parameters:
        app_config (AppConfig): The application configuration object containing the models module.
        **options: Additional keyword arguments, typically
        """

        if app_config.models_module is None:
            return
        connection = connections[options['database']]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options['verbosity'] >= 1:
            self.stderr.write('No sequences found.')
        return '\n'.join(statements)
