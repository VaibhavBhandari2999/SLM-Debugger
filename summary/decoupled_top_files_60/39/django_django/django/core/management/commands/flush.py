from importlib import import_module

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.core.management.sql import emit_post_migrate_signal, sql_flush
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    help = (
        'Removes ALL DATA from the database, including data added during '
        'migrations. Does not achieve a "fresh install" state.'
    )
    stealth_options = ('reset_sequences', 'allow_cascade', 'inhibit_post_migrate')

    def add_arguments(self, parser):
        """
        Function to add command-line arguments to a Django management command.
        
        This function configures the argument parser for a Django management command by adding two optional arguments:
        1. `--noinput` or `--no-input`: A boolean flag that, when set, tells Django not to prompt the user for input of any kind. The default value is `True`.
        2. `--database`: A string that specifies the database to flush. The default value is the 'default' database.
        
        Parameters:
        - parser
        """

        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to flush. Defaults to the "default" database.',
        )

    def handle(self, **options):
        """
        Flush the database tables for the given database.
        
        This function is used to clear all data from the database tables. It accepts several options to control the behavior, such as verbosity, interactive confirmation, and cascade deletion. The function internally handles the flushing process by executing SQL commands to reset the tables to an empty state.
        
        Parameters:
        database (str): The name of the database to flush.
        options (dict): A dictionary containing various options:
        - verbosity (int): Controls the amount of information to
        """

        database = options['database']
        connection = connections[database]
        verbosity = options['verbosity']
        interactive = options['interactive']
        # The following are stealth options used by Django's internals.
        reset_sequences = options.get('reset_sequences', True)
        allow_cascade = options.get('allow_cascade', False)
        inhibit_post_migrate = options.get('inhibit_post_migrate', False)

        self.style = no_style()

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            try:
                import_module('.management', app_config.name)
            except ImportError:
                pass

        sql_list = sql_flush(self.style, connection, only_django=True,
                             reset_sequences=reset_sequences,
                             allow_cascade=allow_cascade)

        if interactive:
            confirm = input("""You have requested a flush of the database.
This will IRREVERSIBLY DESTROY all data currently in the %r database,
and return each table to an empty state.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ % connection.settings_dict['NAME'])
        else:
            confirm = 'yes'

        if confirm == 'yes':
            try:
                connection.ops.execute_sql_flush(database, sql_list)
            except Exception as exc:
                raise CommandError(
                    "Database %s couldn't be flushed. Possible reasons:\n"
                    "  * The database isn't running or isn't configured correctly.\n"
                    "  * At least one of the expected database tables doesn't exist.\n"
                    "  * The SQL was invalid.\n"
                    "Hint: Look at the output of 'django-admin sqlflush'. "
                    "That's the SQL this command wasn't able to run.\n" % (
                        connection.settings_dict['NAME'],
                    )
                ) from exc

            # Empty sql_list may signify an empty database and post_migrate would then crash
            if sql_list and not inhibit_post_migrate:
                # Emit the post migrate signal. This allows individual applications to
                # respond as if the database had been migrated from scratch.
                emit_post_migrate_signal(verbosity, interactive, database)
        else:
            self.stdout.write("Flush cancelled.\n")
