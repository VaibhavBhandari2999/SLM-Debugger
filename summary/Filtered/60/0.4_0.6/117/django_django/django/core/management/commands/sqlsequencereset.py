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
        Reset sequences for all models in the given app configuration.
        
        This function processes the models in the specified app configuration and generates SQL statements to reset the sequences for those models. It takes an `app_config` object, which contains the models module, and an optional `**options` dictionary for additional parameters. The function connects to the specified database and retrieves the models to be processed. It then generates the necessary SQL statements using the connection's operation object. If no sequences are found, a message is printed.
        """

        if app_config.models_module is None:
            return
        connection = connections[options["database"]]
        models = app_config.get_models(include_auto_created=True)
        statements = connection.ops.sequence_reset_sql(self.style, models)
        if not statements and options["verbosity"] >= 1:
            self.stderr.write("No sequences found.")
        return "\n".join(statements)
