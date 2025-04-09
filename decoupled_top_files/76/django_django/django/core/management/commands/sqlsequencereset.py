"""
The provided Python file contains a Django management command named `Command`, which is a subclass of `AppCommand`. The primary purpose of this command is to print SQL statements for resetting sequences for specified Django app models.

#### Main Components:
- **Class**: `Command`
  - **Subclass of**: `AppCommand`
  - **Responsibilities**:
    - Handles the logic for printing SQL statements to reset database sequences.
    - Accepts command-line arguments via the `add_arguments` method.
    - Processes the application configuration using the `handle_app_config` method to generate and print the necessary SQL statements.

- **Methods**:
  - **`add_arguments(parser)`**: Extends the base class method to add a `--database`
"""
from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = 'Prints the SQL statements for resetting sequences for the given app name(s).'

    output_transaction = True

    def add_arguments(self, parser):
        """
        Adds command-line arguments to the argument parser.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the new arguments will be added.
        
        This method extends the functionality of the base class by adding an additional argument `--database` to the parser. The `--database` argument allows specifying a database alias for which the SQL statements should be printed. If no alias is provided, it defaults to the 'default' database.
        """

        super().add_arguments(parser)
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle_app_config(self, app_config, **options):
        """
        Resets database sequences for specified app models.
        
        Args:
        app_config (AppConfig): The application configuration object containing model information.
        **options (dict): Additional keyword arguments, including 'database' and 'verbosity'.
        
        Returns:
        str: A SQL statement string for resetting sequences, or an empty string if no sequences are found.
        
        Summary:
        This function processes the given application configuration to reset database sequences for the specified app models. It uses the `get_models` method to retrieve
        """

        if app_config.models_module is None:
            return
        connection = connections[options['database']]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options['verbosity'] >= 1:
            self.stderr.write('No sequences found.')
        return '\n'.join(statements)
