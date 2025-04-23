from django.core.management.base import AppCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(AppCommand):
    help = (
        "Prints the SQL statements for resetting sequences for the given app name(s)."
    )

    output_transaction = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=(
                'Nominates a database to print the SQL for. Defaults to the "default" '
                "database."
            ),
        )

    def handle_app_config(self, app_config, **options):
        """
        Reset sequences for all models in the given app_config.
        
        This function processes the models specified in the app_config and generates SQL statements to reset the sequences for those models. It takes an app_config object and additional keyword arguments. The app_config should contain the models_module, and the database connection is specified via the 'database' keyword argument. The function outputs a string of SQL statements if any sequences are found, or a message indicating no sequences were found.
        
        Parameters:
        app_config (AppConfig): The
        """

        if app_config.models_module is None:
            return
        connection = connections[options["database"]]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options["verbosity"] >= 1:
            self.stderr.write("No sequences found.")
        return "\n".join(statements)
